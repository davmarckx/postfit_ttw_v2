""" Small macro to combine oviedo's cards and create workspaces """
import re
import argparse
import os
from auxiliars import get_signals, color_msg
import glob


combinerepo = "/user/dmarckx/CMSSW_10_2_16_UL3/src/"

def add_parsing_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analysis', dest = "analysis", default = "oviedo", help = "To select analysis to  take configs.")
    parser.add_argument('--step', dest = "step", default = 1, type = int, help = "1: combinecards, 2:workspace, 3:shapes")
    parser.add_argument('--submit', dest = "submit", action = "store_true", default = False, help = "Submit jobs")
    return parser.parse_args()

def get_combine_cards_cmd(analysis, folder, region, variable):
    varpath = os.path.join( folder, region, variable )

    keyword = "bdt" if analysis == "ghent" else "counting"
    files = [ _file for _file in os.listdir( varpath ) if (".txt" in _file or ".dat" in _file) and "combined" not in _file and "Gen" not in _file]
    #basecmd = 'cmssw-cc7 -B /mnt_pool --command-to-run ' + '" cd {0} && cmsenv && cd {1}; combineCards.py '.format( combinerepo, varpath ) + " ".join( files ) + ' > combined_{0}_{1}_{2}.dat; cd -"'.format( keyword, region, variable )
    basecmd = "cd {0}; cmsenv ; cd {1}; combineCards.py ".format( combinerepo, varpath ) + " ".join( files ) + ' > combined_{0}_{1}_{2}.dat; cd -'.format( keyword, region, variable )
    return basecmd

def get_workspace_cmd(analysis, folder, region, variable):
    
    keyword = "bdt" if analysis == "ghent" else "counting"
    varpath = os.path.join( folder, region, variable )
    combinedcard= "{0}/combined_{1}_{2}_{3}.dat".format( varpath, keyword, region, variable )

     #--PO 'map=.*/TTW1eventBDTnJets:r_TTW1eventBDTnJets[1,0,5]' --PO 'map=.*/TTW2eventBDTnJets:r_TTW2eventBDTnJets[1,0,5]' --PO 'map=.*/TTW3eventBDTnJets:r_TTW3eventBDTnJets[1,0,5]' --PO 'map=.*/TTW4eventBDTnJets:r_TTW4eventBDTnJets[1,0,5]' --PO 'map=.*/TTW5eventBDTnJets:r_TTW5eventBDTnJets[1,0,5]'

    signals = get_signals( combinedcard, analysis, region )
    print('signals are:')
    print(signals)   
 
    if analysis == "ghent":
        # annoying exception: need to combine always with a signal region card because in the variables that do not enter the fit
        # ttw is not marked as signal (it has id > 0)
        if region != "sigreg":
            signals = [signal for signal in signals if "eventBDT" not in signal]

        # Find out which bdt was used
        _fitVariable= re.match(".*_eventBDT(.*)_out.*", glob.glob( varpath + "/*multidim*" )[0]).group(1)
        print("run on: {}".format(_fitVariable))
        
        if '_eventBDT' not in variable: 
          maps = " ".join( [ '--PO "map=.*/{0}.*{1}:r_{0}eventBDT{1}[1,0,5]" '.format( signal.replace(_fitVariable, ""), _fitVariable ) for signal in signals ] )
        elif '_eventBDT' == variable:
           maps = " ".join( [ '--PO "map=.*/{0}.*{1}:r_{0}nJets[1,0,5]" '.format( signal.replace(_fitVariable, ""), _fitVariable ) for signal in signals ] )
        else:
          maps = " ".join( [ '--PO "map=.*/{0}.*{1}:r_{0}{1}[1,0,5]" '.format( signal.replace(_fitVariable, ""), _fitVariable ) for signal in signals ] )
    else:
        maps = " ".join( [ '--PO "map=.*/{0}:r_{0}[1,0,6]" '.format( signal ) for signal in signals ] )


    #basecmd = "cmssw-cc7 -B /mnt_pool --command-to-run ' cd {0} && cmsenv && cd {1}; ulimit -s unlimited; text2workspace.py {2} -o {3}.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose {4}; cd -'".format(combinerepo, varpath, combinedcard.replace(varpath+"/", ""), combinedcard.replace(".dat", "").replace(varpath+"/", ""), maps)
    basecmd = ' cd {0} && cmsenv && cd {1}; ulimit -s unlimited; text2workspace.py {2} -o {3}.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose {4}; cd -'.format(combinerepo, varpath, combinedcard.replace(varpath+"/", ""), combinedcard.replace(".dat", "").replace(varpath+"/", ""), maps)
    return basecmd
 
def get_postfit_cmd(analysis, folder, region, variable):
    
    keyword = "bdt" if analysis == "ghent" else "counting"
    varpath = os.path.join( folder, region, variable )
    combinedcard = "{0}/combined_{1}_{2}_{3}.dat".format( varpath, keyword, region, variable )
    workspace = "{0}/combined_{1}_{2}_{3}.root".format( varpath, keyword, region, variable )

    fitResult = None
    treeName = None
    if analysis == "ghent":
        fitResult = glob.glob( varpath + "/multidim*root" )[0]
        treeName = "fit_mdf"
    if analysis == "oviedo":
        if region != "3l":
          fitResult = glob.glob( varpath.replace(region, "2lss") + "/fitDiagnostics*root" )[0]
        else:
          fitResult = glob.glob( varpath + "/fitDiagnostics*root" )[0]
 
        treeName = "fit_s"

    signals = get_signals( combinedcard, analysis, region )
    #cmd = "sbatch -p batch -e {0}/shapes.%x.%j.err -o {0}/shapes.%x.%j.out --wrap 'cmssw-cc7 -B /mnt_pool/ --command-to-run \"".format( varpath )  + \
    cmd = "cd {0}; cmsenv; cd {1}; ".format(combinerepo, varpath) + \
      " ulimit -s unlimited; " + \
      "PostFitShapesFromWorkspace -w {WSNAME} -d {CARD} ".format( WSNAME = workspace, CARD = combinedcard) + \
      "-o ttW_OUT.root " + \
      "-f {ROOFITRESULT}:{treename} ".format( ROOFITRESULT = fitResult, treename = treeName) + \
      "--postfit --print --total-shapes "

    return cmd 

if __name__ == "__main__":
    
    opts = add_parsing_options()
    analysis = opts.analysis
    submit = opts.submit
    step = opts.step

    # Get a list of variables and regions
    folder = "counting" if analysis == "oviedo" else "bdt" 
    folder = os.path.join( os.getcwd(), folder )
    regions = os.listdir( folder ) 
    variables = []
    for region in regions:
        if not ("3l" == region): continue
        #if region != "cfjetscontrolregion": continue
        print(region)
        #if region != "fourleptoncontrolregion": continue
        color_msg("Region {0}".format(region), color = "green", indentlevel = 0)
        for variable in os.listdir( "{0}/{1}".format( folder, region ) ):
            if "3l" in variable : continue
            color_msg("Variable {0}".format(variable), color = "blue", indentlevel = 1)
            
            if step == 1:
                # get the command for combining cards
                combinecards = get_combine_cards_cmd( analysis, folder, region, variable )
                if opts.submit:
                    os.system( combinecards ) 
                else:
                    print( combinecards )

            if step == 2:
                # Now get the command for the workspaces
                workspace = get_workspace_cmd( analysis, folder, region, variable )
                if opts.submit:
                    os.system( workspace )
                else:
                    print( workspace )

            if step == 3:
                # Now get the command for the postfit shapes
                postfit = get_postfit_cmd( analysis, folder, region, variable )
                if opts.submit:
                    os.system( postfit )
                else:
                    print( postfit )


