import os 
import sys
sys.path.append(os.path.abspath('../ewkino/Tools/python'))
from variabletools import read_variables

variables = read_variables( '/user/dmarckx/ewkino/ttWAnalysis/variables/variables_particlelevel_double.json' )
varnames = [str(var.name) for var in variables]


for varname in varnames:
   os.mkdir('bdt/signalregion/{}'.format(varname))
   os.chdir('bdt/signalregion/{}'.format(varname))

   os.system('cp /user/dmarckx/ewkino/ttWAnalysis/combine/datacards_differential/datacard_signalregion_dilepton_inclusive_run2_{}.* ./'.format(varname))
   os.system('cp /user/dmarckx/ewkino/ttWAnalysis/combine/datacards_differential/histograms_signalregion_dilepton_inclusive_run2_{}.root ./'.format(varname))
   os.system('cp /user/dmarckx/ewkino/ttWAnalysis/combine/datacards_differential/multidimfitdc_combined_{}_out_multidimfit_obs.root ./'.format(varname))

   os.chdir('/user/dmarckx/postfit-ttw')
