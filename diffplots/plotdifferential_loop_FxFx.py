import sys
import os

if __name__=='__main__':

  # arguments
  inputdir = sys.argv[1]
  ssdirbase = sys.argv[2]
  ssfile_oviedo = "fitresults/oviedo/fit_results_2l.json"
  inputdir_FxFx = sys.argv[3]  
  onlyoviedo = False
  tworatios = True
  horizontal = False
 
  regions = {'signalregion_dilepton_inclusive': ssdirbase}# + 'dilepton', 
  #regions = {'signalregion_trilepton': ssdirbase}
  variables = 'variables/variables_particlelevel_single.json'
  #variables = 'variables/variables_particlelevel_single_3l.json'
  writeuncs = False
  write_roots = False

  # basic command
  basiccmd = 'python plotdifferential_FxFx.py --year run2 --processes TTWQCD --xsecs xsecs/xsecs.json'
  basiccmd += ' --variables {}'.format(variables)

  # loop over configurations
  for region,ssdir in regions.items():
    for obstag in ['obs']:
      for crtag in ['withcr']:
        inputfile = os.path.join(inputdir, region, 'particlelevel/merged.root')
        inputfileFxFx = os.path.join(inputdir_FxFx, region, 'particlelevel/merged.root')

        #outputdir = os.path.join(os.path.dirname(inputfile), 'plots_{}_{}'.format(obstag,crtag))
        outputdir = os.path.join("output", 'plots2_{}_{}'.format(obstag,crtag))
        ssfile = os.path.join(ssdir, 'summary_{}_{}.json'.format(obstag, crtag))

        # customize command
        cmd = basiccmd
        cmd += ' --inputfile {}'.format(inputfile)
        cmd += ' --inputfileFxFx {}'.format(inputfileFxFx)
        cmd += ' --outputdir {}'.format(outputdir)
        cmd += ' --signalstrength {}'.format(ssfile)
        cmd += ' --signalstrength_oviedo {}'.format(ssfile_oviedo)
        cmd += ' --region {}'.format(region)
        if write_roots: cmd += ' --write_rootfiles'
        if writeuncs: cmd += ' --writeuncs'
        if onlyoviedo: cmd += ' --onlyoviedo'
        if tworatios and not onlyoviedo: cmd += ' --two_ratiopannels'
        if horizontal: cmd += ' --horizontal'
        # run command
        print('Now running:')
        print(cmd)
        os.system(cmd)
