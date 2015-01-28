#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 256
### Requested computing time in minutes
#SBATCH -t 5:00:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### PHAT
#SBATCH -A TG-AST130057
### Job name
#SBATCH -J 'imf_ap244_miles'
### output and error logs
#SBATCH -o imf_ap244_miles_%j.out
#SBATCH -e imf_ap244_miles_%j.err
ibrun python-mpi prospectr.py --param_file=parfiles/imf_ap244_params.py --outfile=results/ap244_miles_$SLURM_JOB_ID --nwalkers=510 --niter=4096