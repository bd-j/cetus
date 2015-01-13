#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 32
### Requested computing time in minutes
#SBATCH -t 3:00:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### imf
#SBATCH -A TG-AST140054
### PHAT

### Job name
#SBATCH -J 'imf_timing'
### output and error logs
#SBATCH -o imf_timing_%j.out
#SBATCH -e imf_timing_%j.err
export MKL_MIC_ENABLE=1
ibrun python-mpi prospectr.py --param_file=parfiles/imf_timing.py --nwalkers=62
