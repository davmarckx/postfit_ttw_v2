# postfit-ttw

# Run card combination and workspace
```
python3 run_fits --step 1 --analysis $ANALYSIS # card combination
python3 run_fits --step 2 --analysis $ANALYSIS # workspace
python3 run_fits --step 3 --analysis $ANALYSIS # postfit shapes
``` 

Analysis can be `ghent` or  `oviedo`. Adding option `--submit` submits jobs to a slurm cluster using singularity containers. One has to specify the release with the combine code to do the cmsenv. 

# Create plots
```
python3 plot_postfit.py --analysis $ANALYSIS
```

The configs for legends and so on are in `plot_configs.py`. The code is super messy, legends and labels have to be tweaked manually modifying the parameters there. 

