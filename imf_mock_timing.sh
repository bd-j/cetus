#!/bin/bash
### Requested number of nodes
#SBATCH -n 16
### Requested computing time in minutes
#SBATCH -t 1:00:00
###partition
#SBATCH -p normal-mic

### Account
### PHAT
#SBATCH -A TG-AST130057

### Job name
#SBATCH -J 'imf_timing'
### output and error logs
#SBATCH -o imf_timing_wgp_wmkl%j.out
#SBATCH -e imf_timing_wgp_wmkl%j.err
export MKL_MIC_ENABLE=1
ibrun python-mpi prospectr.py --param_file=parfiles/timer_params.py --nwalkers=30
