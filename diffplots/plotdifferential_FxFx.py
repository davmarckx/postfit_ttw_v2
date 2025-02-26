############################################################
# Plot results of a differential cross-section measurement #
############################################################

# Note: the predictions are supposed to be obtained from the scripts 
#       filltheory (for making particle-level histograms) 
#       Note that mergetheory is not applied for this script, this script calculates the normalization itself using
#       hCounter and cross-section (this was done because it is easier to decide what processes to combine and separate, e.g. TTWQCD qnd TTWEWK)

from scipy.stats.distributions import chi2 as chi2_f
import sys
import os
import json
import argparse
import ROOT
import numpy as np
from numpy.linalg import inv
import array
from ROOT import TFile
sys.path.append(os.path.abspath('Tools'))
import histtools as ht
import listtools as lt
import argparsetools as apt
from variabletools import read_variables
sys.path.append(os.path.abspath('plotscripts'))
from differentialplotter import plotdifferential

from processinfo import ProcessInfoCollection, ProcessCollection

from uncertaintyprop import normalizexsec
from uncertaintyprop import sstoxsec
from uncertaintyprop import sstoxsec_oviedo
from scipy import stats


regionmap  = {
    "signalregion_dilepton_inclusive": "2L SR",
    "signalregion_trilepton": "3L SR"
    }

def get_oviedo_name(varname,region="signalregion_dilepton_inclusive"):
  namedict_2l = {
    "_nJets": "njets_7bins",
    "_jetAbsEtaLeading": "jet1_eta",
    "_jetAbsEtaSubLeading": "jet2_eta",
    "_leptonAbsEtaLeading": "lep1_eta",
    "_leptonAbsEtaSubLeading": "lep2_eta",
    "_leptonPtLeading": "lep1_pt",
    "_leptonPtSubLeading": "lep2_pt",
    "_dRl1jet": "mindr_lep1_jet25",
    "_jetPtLeading": "jet1_pt",
    "_jetPtSubLeading": "jet2_pt",
    "_nBJets": "nbjets_medium",
    "_nLooseBjets": "nbjets",
    "_deltaEtaLeadingLeptonPair": "deta_llss",
    "_dRl1l2": "dR_ll",
    "_M3l":"mll",
    "_leptonPtSum": "sum_2lss_pt",
    "_HT": "HT",
    "_leptonMaxEta": "max_eta",
    "_dRl1bjet": "TBD",
    "_bjetAbsEtaLeading": "TBD",
    "_bjetEtaLeading": "TBD",
    "_bjetPtLeading": "TBD",
    "_nMuons": "TBD",
    "_nMuons2": "TBD",
    "_nElectrons": "TBD",
    "_nElectrons2": "TBD",
    "_nBJets2": "nbjets_medium",
    "_nLooseBJets2": "nbjets"
  }

  namedict_3l = {
    "_nJets": "njets_7bins",
    "_jetAbsEtaLeading": "jet1_eta",
    "_jetAbsEtaSubLeading": "jet2_eta",
    "_leptonAbsEtaLeading": "lep1_eta",
    "_leptonAbsEtaSubLeading": "lep2_eta",
    "_leptonPtLeading": "lep1_pt",
    "_leptonPtSubLeading": "lep2_pt",
    "_dRl1jet": "mindr_lep1_jet25",
    "_jetPtLeading": "jet1_pt",
    "_jetPtSubLeading": "jet2_pt",
    "_nBJets": "nbjets_medium",
    "_nLooseBjets": "nbjets",
    "_deltaEtaLeadingLeptonPair": "deta_llss",
    "_dRl1l2": "dR_ll",
    "_M3l":"mll",
    "_leptonPtSum": "pt3l",
    "_HT": "HT",
    "_leptonMaxEta": "max_eta",
    "_dRl1bjet": "TBD",
    "_bjetAbsEtaLeading": "TBD",
    "_bjetEtaLeading": "TBD",
    "_bjetPtLeading": "TBD",
    "_nMuons": "TBD",
    "_nMuons2": "TBD",
    "_nElectrons": "TBD",
    "_nElectrons2": "TBD",
    "_nBJets2": "TBD",
    "_nLooseBJets2": "TBD"
  }

  if region == "signalregion_trilepton":
    return namedict_3l.get(varname,"not implemented in 3l map")
  else:
    return namedict_2l.get(varname,"not implemented in 2l map")

def dict_to_array(d):
  ### convert a 2D dict to an array
  keys = sorted(d.keys())
  nkeys = len(keys)
  a = np.zeros((nkeys,nkeys))
  for i,key1 in enumerate(keys):
    for j,key2 in enumerate(keys):
      a[i,j] = d[key1][key2]
  return a

def gettheocov(variable,isFxFx):
  location = 'cov_oldFxFx/matrix_absolute.json'
  if isFxFx:location = '../nanogendifferential/cov_improvedFxFx/matrix_absolutev2.json'
  else: location = 'cov_oldFxFx/matrix_absolutev2.json'

  with open(location, 'r') as file:
      data = json.load(file)

  matrixup = data[variable]['theoryup_total']
  matrixdown = data[variable]['theoryup_total']

  for i in range(len(matrixup)):
    for j in range(len(matrixup)):
      if (abs(matrixup[i][j]) > abs(matrixdown[i][j])): continue
      matrixup[i][j] = matrixdown[i][j]

  return matrixup

def calcchi2_naive(observedxsec_object, expected):
  ### calculate the chi2 divergence between two histograms
  # note: how to take into account uncertainties?
  chi2 = 0
  ndof = 0

  # get observed xsec
  pois = sorted(observedxsec_object['pois'].keys())
  observed = np.array([observedxsec_object['pois'][poi][0] for poi in pois])
  observed_error = np.array([(abs(observedxsec_object['pois'][poi][3])+abs(observedxsec_object['pois'][poi][4]))/2 for poi in pois])


  for i in range(1, expected.GetNbinsX()+1):
    exp = expected.GetBinContent(i)
    obs = observed[i-1]
    error = expected.GetBinError(i)
    obserror = observed_error[i-1]
    if exp>0:
      chi2 += (obs-exp)**2/(error**2 + obserror**2)
      ndof += 1
  return (chi2_f.sf(chi2,ndof),ndof)

def calcchi2(observedxsec_object, expected,variable,isFxFx=False):
  ### calculate the chi2 divergence between two histograms
  # note: how to take into account uncertainties? => we can get syst enstat cov matrices from the fit, theory cov matrix we calculate by hand using getCovarianceMatrices.py
  # we then use the formula from ttbar multidiff, ttgamma diff (thesis Gianny)
  chi2 = 0
  denom = 0 # needed for normalization chi2
  ndof = 0
  expected = expected.Clone()

  ignoreTheoCov = False
  ignoreStatCov = False
  ignoreSystCov = False

  # get observed xsec
  pois = sorted(observedxsec_object['pois'].keys())
  observed = np.array([observedxsec_object['pois'][poi][0] for poi in pois])

  # get covariances
  covarray_stat_up = dict_to_array(observedxsec_object['statcovup'])
  covarray_stat_down = dict_to_array(observedxsec_object['statcovdown'])
  covarray_syst_up = dict_to_array(observedxsec_object['syscovup'])
  covarray_syst_down = dict_to_array(observedxsec_object['syscovdown'])

  covarray_stat = (covarray_stat_up + covarray_stat_down)/2
  covarray_syst = (covarray_syst_up + covarray_syst_down)/2
  covarray_theo = gettheocov(variable,isFxFx)

  print("covs here rdm:")
  observed = [x*137.61 for x in observed]
  print(observed)
  print("exp:")
  for i in range(0, expected.GetNbinsX()):
    expected.SetBinContent(i+1, expected.GetBinContent(i+1)*137.61)
    print(expected.GetBinContent(i+1))
  print("stat")
  print(covarray_stat)
  print("syst")
  print(covarray_syst)
  print("theo")
  print(covarray_theo)

  #turn off covariances where asked (for testing, is not useful?)
  temp = np.identity(len(covarray_theo))
  if ignoreTheoCov:
    covarray_theo = covarray_theo*temp
  if ignoreStatCov:
    covarray_stat = covarray_stat*temp
  if ignoreSystCov:
    covarray_syst = covarray_syst*temp

  covarray = covarray_stat + covarray_syst + covarray_theo
  covarray *= 137.61*137.61
  covarray_inv = inv(covarray)

  print(covarray)
  print(covarray_inv)

  exp_total = 0
  for i in range(0, expected.GetNbinsX()):
    exp_total += expected.GetBinContent(i+1)
    for j in range(0, expected.GetNbinsX()):
      exp_i = expected.GetBinContent(i+1)
      exp_j = expected.GetBinContent(j+1)
      obs_i = observed[i]
      obs_j = observed[j]

      chi2 += (obs_i-exp_i)*(obs_j-exp_j)*(covarray_inv[i][j])
      denom +=  covarray[i][j]

  chi2_normsubtract = ((np.sum(observed) - exp_total)**2)/denom 
  ndof = expected.GetNbinsX()

  if chi2<0 or chi2_normsubtract<0 or chi2<chi2_normsubtract:
    print("WARNING: either chi2 is negative, chi2_norm is negative or chi2_norm>chi2:")
    print(" * {} * {} * {}".format(chi2<0, chi2_normsubtract<0, chi2<chi2_normsubtract))
    print(chi2)
    print(chi2_normsubtract)

    print("arrays")
    print(covarray_stat)
    print(covarray_syst)
    print(covarray_theo)
    print("denom: {}".format(denom))


  return (chi2,chi2_normsubtract,ndof)


if __name__=='__main__':

  # parse arguments
  parser = argparse.ArgumentParser('Plot differential cross-section')
  parser.add_argument('-i', '--inputfile', required=True, type=os.path.abspath,
                      help='Path to input root file with theoretical differential distributions.')
  parser.add_argument('-i2', '--inputfileFxFx', required=True, type=os.path.abspath,
                      help='Path to input root file with theoretical differential distributions of improved FxFx simulation.')
  parser.add_argument('-y', '--year', required=True,
                      help='Data-taking year (only used for plot aesthetics)')
  parser.add_argument('-r', '--region', required=True)
  parser.add_argument('-p', '--processes', required=True,
                      help='Comma-separated list of process tags to take into account;'
                          +' use "all" to use all processes in the input file.')
  parser.add_argument('-v', '--variables', required=True, type=os.path.abspath,
                      help='Path to json file holding variable definitions.')
  parser.add_argument('-s', '--signalstrength', default=None, type=apt.path_or_none,
                      help='Path to json file holding signal strengths.')
  parser.add_argument('-so', '--signalstrength_oviedo', default=None, type=apt.path_or_none,
                      help='Path to json file holding signal strengths of oviedo.')
  parser.add_argument('-o', '--outputdir', required=True,
                      help='Directory where to store the output.')
  parser.add_argument('--includetags', default=None,
                      help='Comma-separated list of systematic tags to include')
  parser.add_argument('--excludetags', default=None,
                      help='Comma-separated list of systematic tags to exclude')
  parser.add_argument('--tags', default=None,
                      help='Comma-separated list of additional info to display on plot'
                          +' (e.g. simulation year or selection region).'
                          +' Use underscores for spaces.')
  parser.add_argument('--xsecs', required=True, type=os.path.abspath,
                      help='Path to json file holding (predicted) total cross-sections for each process.')
  parser.add_argument('--absolute', default=False, action='store_true',
                      help='If specified, do not divide by bin width,'
                          +' so y-axis unit is in fb instead of fb/GeV.'
                          +' Mostly for testing purposes.')
  parser.add_argument('--onlyoviedo', default=False, action='store_true',
                      help='If specified, draw only the oviedo plots. This is mainly used for the 3l SR results.')
  parser.add_argument('--writeuncs', default=False, action='store_true',
                      help='Write measurement uncertainties in ratio plot')
  parser.add_argument('--write_rootfiles', default=False, action='store_true',
                      help='If specified, rootfiles are written for data'
                          +' by applying the signal strengths.'
                          +' (Only needed for e.g. hepdata submissions.)')
  parser.add_argument('--two_ratiopannels', default=False, action='store_true',
                      help='If specified, two ratiopannels are plotted')
  parser.add_argument('--horizontal', default=False, action='store_true',
                      help='If specified, horizontal line is plotted through data hist')

  args = parser.parse_args()

  # print arguments
  print('Running with following configuration:')
  for arg in vars(args):
    print('  - {}: {}'.format(arg,getattr(args,arg)))

  # parse input file
  if not os.path.exists(args.inputfile):
    raise Exception('ERROR: requested to run on '+args.inputfile
                    +' but it does not seem to exist...')

  # parse the cross-sections
  if not os.path.exists(args.xsecs):
    raise Exception('ERROR: cross-section file '+args.xsecs
                    +' but it does not seem to exist...')
  with open(args.xsecs, 'r') as f:
    xsecs = json.load(f)

  # parse the string with process tags
  processes = args.processes.split(',')
  doallprocesses = (len(processes)==1 and processes[0]=='all')

  # parse the variables
  varlist = read_variables(args.variables)
  variablenames = [v.name for v in varlist]

  # read signal strenght file
  signalstrengths = None
  if args.signalstrength is not None:
    with open(args.signalstrength,'r') as f:
      signalstrengths = json.load(f)

  # read signal strenght file
  signalstrengths_oviedo = {}
  plotoviedo = False
  if args.signalstrength_oviedo is not None:
    with open(args.signalstrength_oviedo,'r') as f:
      signalstrengths_oviedo = json.load(f)
      plotoviedo = True
  # parse include and exclude tags
  includetags = []
  if args.includetags is not None: includetags = args.includetags.split(',')
  excludetags = []
  if args.excludetags is not None: excludetags = args.excludetags.split(',')

  # parse tags
  extratags = []
  if args.tags is not None: extratags = args.tags.split(',')
  extratags = [t.replace('_',' ') for t in extratags]

  # make the output directory
  outputdir = args.outputdir
  if not os.path.exists(outputdir):
    os.makedirs(outputdir)

  region = args.region
  if args.onlyoviedo: region = 'signalregion_trilepton'

  # get all relevant histograms
  print('Loading histogram names from input file...')
  # requirement: the histogram name must contain at least one includetag (or nominal)
  mustcontainone = []
  if len(includetags)>0: mustcontainone = includetags + ['nominal']  + ['hCounter']
  # shortcut requirements for when only one process or variable is requested
  mustcontainall = []
  if( len(processes)==1 and not doallprocesses ): mustcontainall.append(processes[0])
  if len(variablenames)==1: mustcontainall.append(variablenames[0])
  # do loading and initial selection
  histnames = ht.loadhistnames(args.inputfile, mustcontainone=mustcontainone,
                                               maynotcontainone=excludetags,
                                               mustcontainall=mustcontainall)
  print('Initial selection:')
  print(' - mustcontainone: {}'.format(mustcontainone))
  print(' - mustontainall: {}'.format(mustcontainall))
  print(' - maynotcontainone: {}'.format(excludetags))
  print('Resulting number of QCD histograms: {}'.format(len(histnames)))

  mustcontainall = []
  if( len(processes)==1 and not doallprocesses ): mustcontainall.append(processes[0].replace("TTWQCD","TTWEWK"))
  if len(variablenames)==1: mustcontainall.append(variablenames[0])
  # do loading and initial selection
  histnames_EWK = ht.loadhistnames(args.inputfile, mustcontainone=mustcontainone,
                                               maynotcontainone=excludetags,
                                               mustcontainall=mustcontainall)

  print('Resulting number of EWK histograms: {}'.format(len(histnames_EWK)))

  mustcontainall = []
  if( len(processes)==1 and not doallprocesses ): mustcontainall.append(processes[0].replace("TTWQCD","TTWFxFx"))
  if len(variablenames)==1: mustcontainall.append(variablenames[0])
  # do loading and initial selection
  histnames_FxFx = ht.loadhistnames(args.inputfileFxFx, mustcontainone=mustcontainone,
                                               maynotcontainone=excludetags,
                                               mustcontainall=mustcontainall)

  print('Resulting number of improved FxFx histograms: {}'.format(len(histnames_FxFx)))

  # select processes
  if not doallprocesses:
    mustcontainone = ['{}_'.format(p) for p in processes]
    histnames = lt.subselect_strings(histnames, mustcontainone=mustcontainone)[1]
    mustcontainone = ['{}_'.format(p.replace("TTWQCD","TTWEWK")) for p in processes]
    histnames_EWK = lt.subselect_strings(histnames_EWK, mustcontainone=mustcontainone)[1]
    mustcontainone = ['{}_'.format(p.replace("TTWQCD","TTWFxFx")) for p in processes]
    histnames_FxFx = lt.subselect_strings(histnames_FxFx, mustcontainone=mustcontainone)[1]

  # select regions
  mustcontainone = ['_{}_'.format(args.region)]
  histnames = lt.subselect_strings(histnames, mustcontainone=mustcontainone)[1]
  histnames_EWK = lt.subselect_strings(histnames_EWK, mustcontainone=mustcontainone)[1]
  histnames_FxFx = lt.subselect_strings(histnames_FxFx, mustcontainone=mustcontainone)[1]

  # select variables
  histnames = lt.subselect_strings(histnames, mustcontainone=variablenames)[1]
  histnames_EWK = lt.subselect_strings(histnames_EWK, mustcontainone=variablenames)[1]
  histnames_FxFx = lt.subselect_strings(histnames_FxFx, mustcontainone=variablenames)[1]

  print('Further selection (processes, regions and variables):')
  print('Resulting number of QCD histograms: {}'.format(len(histnames)))
  print('Resulting number of EWK histograms: {}'.format(len(histnames_EWK)))
  print('Resulting number of FxFx histograms: {}'.format(len(histnames_FxFx)))

  if len(histnames)<10:
      for histname in histnames: print('  {}'.format(histname))

  # get all hCounter histograms (separate from above)
  mustcontainall = ['hCounter']
  # do loading and initial selection
  hcnames = ht.loadhistnames(args.inputfile, mustcontainall=mustcontainall)

  # make a ProcessInfoCollection to extract information
  # (use first variable, assume list of processes, systematics etc.
  #  is the same for all variables)
  splittag = args.region+'_particlelevel_'+variablenames[0]
  print('Constructing ProcessInfoCollection using split tag "{}"'.format(splittag))
  PIC = ProcessInfoCollection.fromhistlist( histnames, splittag )
  PIC_EWK = ProcessInfoCollection.fromhistlist( histnames_EWK, splittag )
  PIC_FxFx = ProcessInfoCollection.fromhistlist( histnames_FxFx, splittag )

  #print('Constructed following ProcessInfoCollection from histogram list:')
  #print(PIC)

  # get valid processes and compare to arguments
  if doallprocesses:
    processes = sorted(PIC.plist)
  else:
    for p in processes:
      if p not in PIC.plist:
        raise Exception('ERROR: requested process {}'.format(p)
          +' not found in the QCD ProcessInfoCollection.')
      if p.replace("TTWQCD","TTWEWK") not in PIC_EWK.plist:
        raise Exception('ERROR: requested process {}'.format(p)
          +' not found in the EWK ProcessInfoCollection.')
      if p.replace("TTWQCD","TTWFxFx") not in PIC_FxFx.plist:
        raise Exception('ERROR: requested process {}'.format(p)
          +' not found in the FxFx ProcessInfoCollection.')

  print('Extracted following valid process tags from input file:')
  for process in processes: print('  - '+process)

  # get valid systematics and compare to arguments
  shapesyslist = PIC.slist
  print('Extracted following relevant systematics from histogram file:')
  for systematic in shapesyslist: print('  - '+systematic)

  # get the hCounter and cross-sections for each process
  hcounters = []
  xsections = []
  f = ROOT.TFile.Open(args.inputfile,'read')
  for process in [processes[0],processes[0].replace("TTWQCD","TTWEWK")]:
      # get the hCounter
      hcname = str(process+'_'+splittag+'_hCounter')
      if hcname not in (histnames + histnames_EWK):
        msg = 'ERROR: wrong hCounter name:'
        msg += ' histogram {} not found'.format(hcname)
        msg += ' in following list:\n'
        for hname in (histnames + histnames_EWK): msg += '    {}\n'.format(hname)
        raise Exception(msg)
      hcounter = f.Get(hcname)
      hcounter = hcounter.GetBinContent(1)
      hcounters.append(hcounter)
      # get the cross-section
      if process not in xsecs.keys():
        msg = 'ERROR: wrong cross-section:'
        msg += ' process {} not found'.format(process)
        msg += ' in provided dict: {}'.format(xsecs)
        raise Exception(msg)
      xsections.append(xsecs[process]*1000)
      # (factor 1000 is to convert from pb to fb)
  f.Close()

  # get the hCounter and cross-sections for each process in 2nd file
  hcounters2 = []
  xsections2 = []
  f = ROOT.TFile.Open(args.inputfileFxFx,'read')
  for process in [processes[0].replace("TTWQCD","TTWFxFx")]:
      # get the hCounter
      hcname = str(process+'_'+splittag+'_hCounter')
      if hcname not in histnames_FxFx:
        msg = 'ERROR: wrong hCounter name:'
        msg += ' histogram {} not found'.format(hcname)
        msg += ' in following list:\n'
        for hname in histnames: msg += '    {}\n'.format(hname)
        raise Exception(msg)
      hcounter = f.Get(hcname)
      hcounter = hcounter.GetBinContent(1)
      hcounters2.append(hcounter)
      # get the cross-section
      if process not in xsecs.keys():
        msg = 'ERROR: wrong cross-section:'
        msg += ' process {} not found'.format(process)
        msg += ' in provided dict: {}'.format(xsecs)
        raise Exception(msg)
      xsections2.append(xsecs[process]*1000)
      # (factor 1000 is to convert from pb to fb)
  f.Close()


  # if we want a collection of data histograms we initialize the root file here
  if args.write_rootfiles:
    if not os.path.exists(os.path.join(outputdir,"rootfiles")):
        os.makedirs(os.path.join(outputdir,"rootfiles"))
    rootfilename = os.path.join(outputdir,"rootfiles/differentialplots_{}.root".format(args.year))
    rootfile = TFile( rootfilename, 'RECREATE' )

  # loop over variables
  for var in varlist:
    if "BJets" in var.name: continue
    # get name and title
    variablename = var.name
    xaxtitle = var.axtitle
    if var.unit is not None: xaxtitle += ' ({})'.format(var.unit)
    print('Now running on variable {}...'.format(variablename))

    # extra histogram selection for overlapping variable names
    othervarnames = [v.name for v in varlist if v.name!=variablename]
    thishistnames = lt.subselect_strings(histnames,
                      mustcontainall=[variablename],
                      maynotcontainone=['_{}_'.format(el) for el in othervarnames])[1]

    thishistnames_EWK = lt.subselect_strings(histnames_EWK,
                      mustcontainall=[variablename],
                      maynotcontainone=['_{}_'.format(el) for el in othervarnames])[1]

    thishistnames_FxFx = lt.subselect_strings(histnames_FxFx,
                      mustcontainall=[variablename],
                      maynotcontainone=['_{}_'.format(el) for el in othervarnames])[1]

    # make a ProcessCollection for this variable
    splittag = args.region+'_particlelevel_'+variablename
    PIC = ProcessInfoCollection.fromhistlist( thishistnames, splittag )
    PC = ProcessCollection( PIC, args.inputfile )
    hcounter = hcounters[0]
    xsection = xsections[0]
    scale = xsection/hcounter
    for hist in PC.get_allhists():
      hist.Scale(scale)

    PIC_FxFx = ProcessInfoCollection.fromhistlist( thishistnames_FxFx, splittag )
    PC_FxFx = ProcessCollection( PIC_FxFx, args.inputfileFxFx )
    hcounter = hcounters2[0]
    xsection = xsections2[0]
    scale = xsection/hcounter
    for hist in PC_FxFx.get_allhists():
      hist.Scale(scale)

    PIC_EWK = ProcessInfoCollection.fromhistlist( thishistnames_EWK, splittag )
    PC_EWK = ProcessCollection( PIC_EWK, args.inputfile )
    hcounter = hcounters[1]
    xsection = xsections[1]
    scale = xsection/hcounter
    for hist in PC_EWK.get_allhists():
      hist.Scale(scale)

    # make some copies of reference histograms before dividing by bin width
    # (note: do not forget to scale by xsec and lumi below!)
    nominalrefs = []
    nominalrefs_EWK = []
    nominalrefs_FxFx = []

    for process in processes:
      nominalrefs.append( PC.processes[process].get_nominal().Clone() )
      nominalrefs_EWK.append( PC_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_nominal().Clone() )
      nominalrefs_FxFx.append( PC_FxFx.processes[process.replace("TTWQCD","TTWFxFx")].get_nominal().Clone() )

    # divide bin contents by bin widths in all histograms
    if not args.absolute:
      for hist in PC.get_allhists():
        for i in range(1,hist.GetNbinsX()+1):
          binwidth = hist.GetBinWidth(i)
          hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
          hist.SetBinError(i, hist.GetBinError(i)/binwidth)
      for hist in PC_EWK.get_allhists():
        for i in range(1,hist.GetNbinsX()+1):
          binwidth = hist.GetBinWidth(i)
          hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
          hist.SetBinError(i, hist.GetBinError(i)/binwidth)
      for hist in PC_FxFx.get_allhists():
        for i in range(1,hist.GetNbinsX()+1):
          binwidth = hist.GetBinWidth(i)
          hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
          hist.SetBinError(i, hist.GetBinError(i)/binwidth)

    # make a second ProcessCollection and normalize all its histograms
    # to unit surface area
    PC_norm = ProcessCollection( PIC, args.inputfile )
    for hist in PC_norm.get_allhists():
      if not args.absolute:
        for i in range(1,hist.GetNbinsX()+1):
          binwidth = hist.GetBinWidth(i)
          hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
          hist.SetBinError(i, hist.GetBinError(i)/binwidth)
        hist.Scale(1./hist.Integral('width'))
      else:
        hist.Scale(1./hist.Integral())
    PC_norm_EWK = ProcessCollection( PIC_EWK, args.inputfile )
    for hist in PC_norm_EWK.get_allhists():
      if not args.absolute:
        for i in range(1,hist.GetNbinsX()+1):
          binwidth = hist.GetBinWidth(i)
          hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
          hist.SetBinError(i, hist.GetBinError(i)/binwidth)
        hist.Scale(1./hist.Integral('width'))
      else:
        hist.Scale(1./hist.Integral())
    PC_norm_FxFx = ProcessCollection( PIC_FxFx, args.inputfileFxFx )
    for hist in PC_norm_FxFx.get_allhists():
      if not args.absolute:
        for i in range(1,hist.GetNbinsX()+1):
          binwidth = hist.GetBinWidth(i)
          hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
          hist.SetBinError(i, hist.GetBinError(i)/binwidth)
        hist.Scale(1./hist.Integral('width'))
      else:
        hist.Scale(1./hist.Integral())
    
    # get one nominal and one total systematic histogram for each process         <======
    nominalhists = []
    systhists = []
    systematics = ['pdfTotalRMS','rfScalesTotal','isrTotal','fsrTotal']
    #systematics = []
    #print('WARNING: list of systematics set to empty for testing.')
    for process in processes:
      # add QCD
      nominalhist = PC.processes[process].get_nominal()
      nominalhist.SetTitle( "aMC@NLO+PY8")# (FxFx arXiv:1209.6215)" ) #process.split('_')[0]) 
      rsshist = PC.processes[process].get_systematics_rss(systematics=systematics)
      systhist = nominalhist.Clone()
      for i in range(0, nominalhist.GetNbinsX()+2):
        systhist.SetBinError(i, rsshist.GetBinContent(i))


      #nominalhists.append(nominalhist)
      #systhists.append(systhist)

      nominalhist_withEWK = PC_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_nominal().Clone()
      nominalhist_withEWK.SetTitle( "aMC@NLO+PY8 (FxFx arXiv:1209.6215)" )
      nominalhist_withEWK.Add(nominalhist)
      rsshist_EWK = PC_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_systematics_rss(systematics=systematics)

      systhist_withEWK = nominalhist_withEWK.Clone()
      for i in range(0, nominalhist_withEWK.GetNbinsX()+2):
        systhist_withEWK.SetBinError(i, np.sqrt(rsshist_EWK.GetBinContent(i)**2 + rsshist.GetBinContent(i)**2))

      nominalhists.append(nominalhist_withEWK)
      systhists.append(systhist_withEWK)

      fxfxhist_withEWK = PC_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_nominal().Clone()

      fxfxhist_withEWK.SetTitle( "aMC@NLO+PY8 (FxFx arXiv:2108.07826)" )
      QCDhist = PC_FxFx.processes[process.replace("TTWQCD","TTWFxFx")].get_nominal().Clone()

      fxfxhist_withEWK.Add(QCDhist)
      rsshist_EWK = PC_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_systematics_rss(systematics=systematics)
      rsshist_FxFx = PC_FxFx.processes[process.replace("TTWQCD","TTWFxFx")].get_systematics_rss(systematics=systematics)

      systhist_withFxFx = fxfxhist_withEWK.Clone()
      for i in range(0, fxfxhist_withEWK.GetNbinsX()+2):
        systhist_withFxFx.SetBinError(i, np.sqrt(rsshist_EWK.GetBinContent(i)**2 + rsshist_FxFx.GetBinContent(i)**2))

      nominalhists.append(fxfxhist_withEWK)
      systhists.append(systhist_withFxFx)


    # do the same for normalized histograms
    nominalhists_norm = []
    systhists_norm = []
    for process in processes:
      nominalhist = PC_norm.processes[process].get_nominal()
      nominalhist.SetTitle( "NLO QCD (FxFx arXiv:1209.6215)" )#process.split('_')[0] )
      rsshist = PC_norm.processes[process].get_systematics_rss(systematics=systematics)
      systhist = nominalhist.Clone()
      for i in range(0, nominalhist.GetNbinsX()+2):
        systhist.SetBinError(i, rsshist.GetBinContent(i))

      nominalhist_withEWK = PC_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_nominal().Clone()
      nominalhist_withEWK.SetTitle( "NLO QCD + EWK (FxFx arXiv:1209.6215)" )
      QCDhist = PC.processes[process].get_nominal().Clone()

      nominalhist_withEWK.Add(QCDhist)

      # scale it to 1
      if not args.absolute:
        nominalhist_withEWK.Scale(1./nominalhist_withEWK.Integral('width'))
      else:
        nominalhist_withEWK.Scale(1./nominalhist_withEWK.Integral())      

      rsshist_EWK = PC_norm_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_systematics_rss(systematics=systematics)

      systhist_withEWK = nominalhist_withEWK.Clone()
      for i in range(0, nominalhist_withEWK.GetNbinsX()+2):
        systhist_withEWK.SetBinError(i, np.sqrt(rsshist_EWK.GetBinContent(i)**2 + rsshist.GetBinContent(i)**2))

      nominalhists_norm.append(nominalhist_withEWK)
      systhists_norm.append(systhist_withEWK)


      fxfxhist_withEWK = PC_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_nominal().Clone()
      fxfxhist_withEWK.SetTitle( "NLO QCD + EWK (FxFx  arXiv:2108.07826)" )
      QCDhist = PC_FxFx.processes[process.replace("TTWQCD","TTWFxFx")].get_nominal().Clone()

      fxfxhist_withEWK.Add(QCDhist)

      # scale it to 1
      if not args.absolute:
        fxfxhist_withEWK.Scale(1./fxfxhist_withEWK.Integral('width'))
      else:
        fxfxhist_withEWK.Scale(1./fxfxhist_withEWK.Integral())

      rsshist_EWK = PC_norm_EWK.processes[process.replace("TTWQCD","TTWEWK")].get_systematics_rss(systematics=systematics)
      rsshist_FxFx = PC_norm_FxFx.processes[process.replace("TTWQCD","TTWFxFx")].get_systematics_rss(systematics=systematics)

      systhist_withEWK = fxfxhist_withEWK.Clone()
      for i in range(0, nominalhist_withEWK.GetNbinsX()+2):
        systhist_withEWK.SetBinError(i, np.sqrt(rsshist_EWK.GetBinContent(i)**2 + rsshist_FxFx.GetBinContent(i)**2))

      nominalhists_norm.append(fxfxhist_withEWK)
      systhists_norm.append(systhist_withEWK)


    # find signal strengths
    datahist = nominalrefs[0].Clone()
    datahist.Add(nominalrefs_EWK[0].Clone())
    statdatahist = datahist.Clone()
    normdatahist = datahist.Clone()
    normstatdatahist = datahist.Clone()

    datahist_oviedo = nominalrefs[0].Clone()
    datahist_oviedo.Add(nominalrefs_EWK[0].Clone())
    statdatahist_oviedo = datahist.Clone()
    normdatahist_oviedo = datahist.Clone()
    normstatdatahist_oviedo = datahist.Clone()



    dochi2 = False # disable for now
    if signalstrengths is None:
      dochi2 = False
      datahist.Reset()
      statdatahist.Reset()
      normdatahist.Reset()
      normstatdatahist.Reset()
      
      datahist_oviedo.Reset()
      statdatahist_oviedo.Reset()
      normdatahist_oviedo.Reset()
      normstatdatahist_oviedo.Reset()
    else:
      thisss = signalstrengths.get(variablename,None)
      if thisss is None:
        dochi2 = False
        msg = 'ERROR: variable {} not found in signal strengths,'.format(variablename)
        msg += ' setting data to zero.'
        print(msg)
        datahist.Reset()
        statdatahist.Reset()
        normdatahist.Reset()
        normstatdatahist.Reset()
      elif len(thisss['pois'])!=datahist.GetNbinsX():
        dochi2 = False
        msg = 'ERROR: number of signal strengths and number of bins do not agree'
        msg += ' for variable {},'.format(variablename)
        msg += ' setting data to zero.'
        print(msg)
        datahist.Reset()
        statdatahist.Reset()
        normdatahist.Reset()
        normstatdatahist.Reset()
      else:
        # check if we have oviedo signalstrengths
        oviedoss = signalstrengths_oviedo.get(get_oviedo_name(variablename,region),None)
        if oviedoss is None:
          plotoviedo = False
          oviedoss = thisss
          msg = 'ERROR: variable {} not found in oviedo signal strengths,'.format(get_oviedo_name(variablename))
          msg += ' setting oviedo data to zero.'
          print(msg)
          datahist_oviedo.Reset()
          statdatahist_oviedo.Reset()
          normdatahist_oviedo.Reset()
          normstatdatahist_oviedo.Reset()
        elif len(oviedoss['pois'])!=datahist.GetNbinsX():
          plotoviedo = False
          oviedoss = thisss
          msg = 'ERROR: number of signal strengths ({}) and number of bins ({}) do not agree'.format(len(oviedoss),datahist.GetNbinsX())
          msg += ' for variable {},'.format(variablename)
          msg += ' setting oviedo data to zero.'
          print(msg)
          datahist_oviedo.Reset()
          statdatahist_oviedo.Reset()
          normdatahist_oviedo.Reset()
          normstatdatahist_oviedo.Reset()  

        else:
          plotoviedo = True

        # convert signal strengths to absolute cross sections
        # (note: not divided by bin width, so values in fb)
        print("now making the oviedo xsecs")
        pred = {}
        pred_oviedo = {}
        for i in range(1, nominalrefs[0].GetNbinsX()+1):
          pred['r_TTW{}{}'.format(i,variablename.strip('_'))] = datahist.GetBinContent(i)
          pred_oviedo['r_TTW_{}_bin{}'.format(get_oviedo_name(variablename,region), i-1)] = datahist.GetBinContent(i)
        thisxsec = sstoxsec(thisss, pred)

        if plotoviedo: oviedoxsec = sstoxsec_oviedo(oviedoss, pred_oviedo)
        else:          oviedoxsec = sstoxsec(oviedoss, pred)


        # fill the histograms for absolute cross sections
        for i in range(1, datahist.GetNbinsX()+1):
          poi = 'r_TTW{}{}'.format(i,variablename.strip('_'))
          if len(thisxsec['pois'][poi])==3:
            error = max(thisxsec['pois'][poi][1], thisxsec['pois'][poi][2])
            staterror = 0
          elif len(thisxsec['pois'][poi])==5:
            error = max(thisxsec['pois'][poi][3], thisxsec['pois'][poi][4])
            staterror = max(thisxsec['pois'][poi][1], thisxsec['pois'][poi][2])
          datahist.SetBinContent(i, thisxsec['pois'][poi][0])
          datahist.SetBinError(i, error)
          statdatahist.SetBinContent(i, thisxsec['pois'][poi][0])
          statdatahist.SetBinError(i, staterror)

          if plotoviedo:
           poi = 'r_TTW_{}_bin{}'.format(get_oviedo_name(variablename,region),i-1)
           if len(oviedoxsec['pois'][poi])==3:
             error = max(oviedoxsec['pois'][poi][1], oviedoxsec['pois'][poi][2])
             staterror = 0
           elif len(oviedoxsec['pois'][poi])==5:
             error = max(oviedoxsec['pois'][poi][3], oviedoxsec['pois'][poi][4])
             staterror = max(oviedoxsec['pois'][poi][1], oviedoxsec['pois'][poi][2])
           datahist_oviedo.SetBinContent(i, oviedoxsec['pois'][poi][0])
           datahist_oviedo.SetBinError(i, error)
           statdatahist_oviedo.SetBinContent(i, oviedoxsec['pois'][poi][0])
           statdatahist_oviedo.SetBinError(i, staterror)

        # calculate normalized cross-sections
        thisnormxsec = normalizexsec(thisxsec)
        oviedonormxsec = normalizexsec(oviedoxsec)
        print(thisnormxsec)
        print(oviedonormxsec)


        # fill normalized histograms
        for i in range(1, normdatahist.GetNbinsX()+1):
          poi = 'r_TTW{}{}'.format(i,variablename.strip('_'))
          if len(thisnormxsec[poi])==3:
            error = max(thisnormxsec[poi][1], thisnormxsec[poi][2])
            staterror = 0
          elif len(thisnormxsec[poi])==5:
            errordown = (thisnormxsec[poi][1]**2 + thisnormxsec[poi][3]**2)**(0.5)
            errorup = (thisnormxsec[poi][2]**2 + thisnormxsec[poi][4]**2)**(0.5)
            error = max(errordown, errorup)
            staterror = max(thisnormxsec[poi][1], thisnormxsec[poi][2])
          
          normdatahist.SetBinContent(i, thisnormxsec[poi][0])
          normdatahist.SetBinError(i, error)
          normstatdatahist.SetBinContent(i, thisnormxsec[poi][0])
          normstatdatahist.SetBinError(i, staterror)
          if plotoviedo:
           poi = 'r_TTW_{}_bin{}'.format(get_oviedo_name(variablename,region),i-1)
           if len(oviedonormxsec[poi])==3:
             error = max(oviedonormxsec[poi][1], oviedonormxsec[poi][2])
             staterror = 0
           elif len(oviedonormxsec[poi])==5:
             errordown = (oviedonormxsec[poi][1]**2 + oviedonormxsec[poi][3]**2)**(0.5)
             errorup = (oviedonormxsec[poi][2]**2 + oviedonormxsec[poi][4]**2)**(0.5)
             error = max(errordown, errorup)
             staterror = max(oviedonormxsec[poi][1], oviedonormxsec[poi][2])
           else:
             msg = 'ERROR: length of normalized oviedo xsec ({}) and expected nr (3 or 5) do not agree'.format(len(oviedonormxsec))
             msg += ' for variable {},'.format(variablename)
             msg += ' setting oviedo data to zero.'
             print(msg)
             plotoviedo = False
           normdatahist_oviedo.SetBinContent(i, oviedonormxsec[poi][0])
           normdatahist_oviedo.SetBinError(i, error)
           normstatdatahist_oviedo.SetBinContent(i, oviedonormxsec[poi][0])
           normstatdatahist_oviedo.SetBinError(i, staterror)

        # divide by bin width
        if not args.absolute:
          for hist in [datahist, statdatahist, normdatahist, normstatdatahist]:
            for i in range(1,hist.GetNbinsX()+1):
              binwidth = hist.GetBinWidth(i)
              hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
              hist.SetBinError(i, hist.GetBinError(i)/binwidth)
          if plotoviedo:
           for hist in [datahist_oviedo, statdatahist_oviedo, normdatahist_oviedo, normstatdatahist_oviedo]:
            for i in range(1,hist.GetNbinsX()+1):
              binwidth = hist.GetBinWidth(i)
              hist.SetBinContent(i, hist.GetBinContent(i)/binwidth)
              hist.SetBinError(i, hist.GetBinError(i)/binwidth) 

    # make extra infos to display on plot
    print(args.region)
    print(regionmap[args.region])
    extrainfos = [regionmap[args.region]]
    chi2info_old = []
    chi2info_improved = []

    chi2info_old_norm = []
    chi2info_improved_norm = []

    for tag in extratags: extrainfos.append(tag)

    if dochi2:
      nominalrefQCD_forchi2 = nominalrefs[0].Clone()
      nominalrefQCD_forchi2.Add(nominalrefs_EWK[0].Clone())

      nominalrefFxFx_forchi2 = nominalrefs_FxFx[0].Clone()
      nominalrefFxFx_forchi2.Add(nominalrefs_EWK[0].Clone())
      nominalrefs_forchi2 = [nominalrefQCD_forchi2, nominalrefFxFx_forchi2]
      for nominalhist in nominalrefs_forchi2:
        #print(nominalhist.GetName())
        #print(nominalhist.GetTitle())
        FxFxflag = False
        if 'TTWFxFx' == nominalhist.GetTitle(): FxFxflag = True
       
        print("thisisus")
        (chi2_naive,ndof) = calcchi2_naive(thisxsec,nominalhist)
        (chi2,chi2_normsubtract,ndof) = calcchi2(thisxsec,nominalhist,variablename,isFxFx=FxFxflag)
        #print(chi2)
        #print(chi2_normsubtract)

        chi2info = '#chi2 / ndof = {:.4f}/{}'.format(chi2_f.sf(chi2,ndof), ndof)
     
        if FxFxflag:
          extrainfos.append("we naive: {:.4f}, {}".format(chi2_naive,ndof) )
          chi2info_improved.append(chi2info)
          chi2info_improved_norm.append('#chi2 / ndof-1 = {:.4f}/{}'.format(chi2_f.sf((chi2-chi2_normsubtract),( ndof-1)),ndof-1))
        else:
          chi2info_old.append("{:.4f}".format(chi2_f.sf(chi2,ndof)))
          chi2info_old_norm.append("{:.4f}".format(chi2_f.sf(chi2-chi2_normsubtract,ndof-1)))
 

        if plotoviedo:
          print("oviedo here")
          print(oviedoxsec)
          (chi2_naive,ndof) = calcchi2_naive(oviedoxsec,nominalhist)
          print("thisisoviedo")
          (chi2,chi2_normsubtract,ndof) = calcchi2(oviedoxsec,nominalhist,variablename,isFxFx=FxFxflag)

          chi2info = '#p = {:.3f}/{}'.format(chi2_f.sf(chi2,ndof),ndof)

          if FxFxflag: 
            extrainfos.append("oviedo naive: {:.3f}/{}".format(chi2_naive,ndof))
            chi2info_improved.append(chi2info)
            chi2info_improved_norm.append('#c2/n={:.3f}/{} pval={:.3f}'.format(chi2_f.sf((chi2-chi2_normsubtract),( ndof-1)),ndof, 1 - stats.chi2.cdf(chi2-chi2_normsubtract, ndof-1)))

          else: 
            chi2info_old.append("{:.4f}".format(chi2_f.sf(chi2,ndof)))
            chi2info_old_norm.append("{:.4f}".format(chi2_f.sf(chi2-chi2_normsubtract,ndof-1)))


    # set plot properties
    figname = variablename
    figname = os.path.join(outputdir,figname)
    yaxdenom = var.axtitle
    if var.shorttitle is not None: yaxdenom = var.shorttitle
    yaxunit = '\\text{fb}'
    if var.unit is not None: yaxunit += '/\\text{'+str(var.unit)+"}"
    yaxunit_norm = ''
    if var.unit is not None: yaxunit_norm = '(1/\\text{'+str(var.unit)+'})'
    yaxtitle = 'd\\sigma / d{} ({})'.format(yaxdenom,yaxunit)
    yaxtitle_norm = '1/\\sigma d\\sigma / d{} {}'.format(yaxdenom,yaxunit_norm)
    if args.absolute:
      yaxunit = 'fb'
      yaxtitle = '#sigma ({})'.format(yaxunit)
      yaxtitle_norm = '#sigma (normalized)'
    extracmstext = ''

    # set lumi value to display
    lumimap = {'run2':137600, '2016':36300, '2017':41500, '2018':59700,
                    '2016PreVFP':19520, '2016PostVFP':16810 }
    lumitext = ''
    if args.year is not None:
      if not args.year in lumimap.keys():
        print('WARNING: year {} not recognized,'.format(args.year)
              +' will not write lumi header.')
      lumi = lumimap.get(args.year,None)
      if lumi is not None: lumitext = '{0:.3g}'.format(lumi/1000.)+' fb^{-1} (13 TeV)'

    # temporary for plots: change label for legend
    # (to do more cleanly later)
    for hist in nominalhists + nominalhists_norm:
      title = hist.GetTitle()
      title = title.replace('2018','')
      title = title.replace('EFT',' ')
      #title += ' pred.'
      hist.SetTitle(title)
    if len(nominalhists)==1:
        nominalhists[0].SetTitle('Prediction')
    if len(nominalhists_norm)==1:
        nominalhists_norm[0].SetTitle('Prediction')

    if not plotoviedo:
     datahist_oviedo = None
     statdatahist_oviedo = None
     mormdatahist_oviedo = None
     normstatdatahist_oviedo = None

    # shift bins a bit to make both data visible
    if plotoviedo and not args.onlyoviedo:
      binedges = []
      for i in range(0, datahist_oviedo.GetNbinsX()+1):
        binedges.append(datahist_oviedo.GetXaxis().GetXbins().At(i))

      offset = (binedges[-1] - binedges[0])/50
      binedges_low = array.array('d', [x-offset for x in binedges])
      binedges_high = array.array('d', [x+offset for x in binedges])

      # our hists
      dummyhist = ROOT.TH1D(datahist.GetName(),datahist.GetTitle(),len(binedges)-1, binedges_low)
      for i in range(1, datahist.GetNbinsX()+1):
            dummyhist.SetBinError(i,datahist.GetBinError(i))
            dummyhist.SetBinContent(i,datahist.GetBinContent(i))

      datahist = dummyhist.Clone()

      statdummyhist = ROOT.TH1D(statdatahist.GetName(),statdatahist.GetTitle(),len(binedges)-1, binedges_low)
      for i in range(1, statdatahist.GetNbinsX()+1):
            statdummyhist.SetBinError(i,statdatahist.GetBinError(i))
            statdummyhist.SetBinContent(i,statdatahist.GetBinContent(i))

      statdatahist = statdummyhist.Clone()

      normdummyhist = ROOT.TH1D(normdatahist.GetName(),normdatahist.GetTitle(),len(binedges)-1, binedges_low)
      for i in range(1, normdatahist.GetNbinsX()+1):
            normdummyhist.SetBinError(i,normdatahist.GetBinError(i))
            normdummyhist.SetBinContent(i,normdatahist.GetBinContent(i))

      normdatahist = normdummyhist.Clone()

      normstatdummyhist = ROOT.TH1D(normstatdatahist.GetName(),normstatdatahist.GetTitle(),len(binedges)-1, binedges_low)
      for i in range(1, normstatdatahist.GetNbinsX()+1):
            normstatdummyhist.SetBinError(i,normstatdatahist.GetBinError(i))
            normstatdummyhist.SetBinContent(i,normstatdatahist.GetBinContent(i))

      normstatdatahist = normstatdummyhist.Clone()

      # oviedo hists 
      dummyhist_oviedo = ROOT.TH1D(datahist_oviedo.GetName(),datahist_oviedo.GetTitle(),len(binedges)-1, binedges_high)
      for i in range(1, datahist_oviedo.GetNbinsX()+1):
            dummyhist_oviedo.SetBinError(i,datahist_oviedo.GetBinError(i))
            dummyhist_oviedo.SetBinContent(i,datahist_oviedo.GetBinContent(i))

      datahist_oviedo = dummyhist_oviedo.Clone()

      statdummyhist_oviedo = ROOT.TH1D(statdatahist_oviedo.GetName(),statdatahist_oviedo.GetTitle(),len(binedges)-1, binedges_high)
      for i in range(1, statdatahist_oviedo.GetNbinsX()+1):
            statdummyhist_oviedo.SetBinError(i,statdatahist_oviedo.GetBinError(i))
            statdummyhist_oviedo.SetBinContent(i,statdatahist_oviedo.GetBinContent(i))

      statdatahist_oviedo = statdummyhist_oviedo.Clone()

      normdummyhist_oviedo = ROOT.TH1D(normdatahist_oviedo.GetName(),normdatahist_oviedo.GetTitle(),len(binedges)-1, binedges_high)
      for i in range(1, normdatahist_oviedo.GetNbinsX()+1):
            normdummyhist_oviedo.SetBinError(i,normdatahist_oviedo.GetBinError(i))
            normdummyhist_oviedo.SetBinContent(i,normdatahist_oviedo.GetBinContent(i))

      normdatahist_oviedo = normdummyhist_oviedo.Clone()

      normstatdummyhist_oviedo = ROOT.TH1D(normstatdatahist_oviedo.GetName(),normstatdatahist_oviedo.GetTitle(),len(binedges)-1, binedges_high)
      for i in range(1, normstatdatahist_oviedo.GetNbinsX()+1):
            normstatdummyhist_oviedo.SetBinError(i,normstatdatahist_oviedo.GetBinError(i))
            normstatdummyhist_oviedo.SetBinContent(i,normstatdatahist_oviedo.GetBinContent(i))

      normstatdatahist_oviedo = normstatdummyhist_oviedo.Clone()

    if args.onlyoviedo and plotoviedo:
      #switch histograms (boolean is also given to change name)
      datahist = datahist_oviedo.Clone()
      statdatahist = statdatahist_oviedo.Clone()
      mormdatahist = normdatahist_oviedo.Clone()
      normstatdatahist = normstatdatahist_oviedo.Clone()

      datahist_oviedo = None
      statdatahist_oviedo = None
      mormdatahist_oviedo = None
      normstatdatahist_oviedo = None

    if not dochi2:
      chi2info_improved=['','']
      chi2info_old = ['','']
      chi2info_improved_norm=['','']
      chi2info_old_norm = ['','']

    # make the plot
    plotdifferential(
        nominalhists, datahist,
	systhists=systhists,
        statdatahist=statdatahist,
        datahist_oviedo=datahist_oviedo,
        statdatahist_oviedo=statdatahist_oviedo,
	figname=figname+'',
        yaxtitle=yaxtitle, xaxtitle=xaxtitle,
        drawoptions='hist ][',
        extracmstext=extracmstext,
        lumitext=lumitext,ratiorange=(0.5,1.5),
        extrainfos=extrainfos, infosize=15,
        chi2info_old=chi2info_old,
        chi2info_improved=chi2info_improved,
        writeuncs=args.writeuncs,
        onlyoviedo = args.onlyoviedo,
        two_ratiopannels = args.two_ratiopannels,
        horizontal = args.horizontal )

    # make the plot with normalized distributions
    figname_norm = figname+'_norm'
    plotdifferential(
        nominalhists_norm, normdatahist,
        systhists=systhists_norm,
        statdatahist=normstatdatahist,
        datahist_oviedo=normdatahist_oviedo,
        statdatahist_oviedo=normstatdatahist_oviedo,
        figname=figname_norm,
        yaxtitle=yaxtitle_norm, xaxtitle=xaxtitle,
        drawoptions='hist ][',
        extracmstext=extracmstext,
        lumitext=lumitext,ratiorange=(0.2,1.8),
        extrainfos=extrainfos, infosize=15,
        chi2info_old=chi2info_old_norm,
        chi2info_improved=chi2info_improved_norm,
        writeuncs=args.writeuncs,
        onlyoviedo = args.onlyoviedo,
        two_ratiopannels = args.two_ratiopannels,
        horizontal = args.horizontal  )
    
    # we write the histograms if requested
    if args.write_rootfiles:
        rootfile.cd()
        print("Writing data histograms to {}...".format(rootfile))
        datahist.SetName( datahist.GetName().replace("nominal","data"))
        datahist.Write()
        statdatahist.SetName( statdatahist.GetName().replace("nominal","datastat"))
        statdatahist.Write()
        normdatahist.SetName( normdatahist.GetName().replace("nominal","normdata"))
        normdatahist.Write()
        normstatdatahist.SetName( normstatdatahist.GetName().replace("nominal","normstatdata"))
        normstatdatahist.Write()
        print("Writing theory histograms...")
        if len(nominalhists) == 1:
            nominalhists[0].SetName( nominalhists[0].GetName().replace("nominal","MC"))
            nominalhists[0].Write()
            nominalhists_norm[0].SetName( nominalhists_norm[0].GetName().replace("nominal","normMC"))
            nominalhists_norm[0].Write()
        if len(systhists) == 1:    
            systhists[0].SetName( systhists[0].GetName().replace("nominal","MC_syst"))
            systhists[0].Write()
            systhists_norm[0].SetName( systhists_norm[0].GetName().replace("nominal","normMC_syst"))
            systhists_norm[0].Write()
        elif len(nominalhists) != 1 or len(systhists) != 1:
            print("WARNING: one theory histogram was expected so theory histograms aren't written!")


  # close rootfile if it was requested
  if args.write_rootfiles:
     rootfile.Close()
