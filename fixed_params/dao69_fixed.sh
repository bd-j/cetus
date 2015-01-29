#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 128
### Requested computing time in minutes
#SBATCH -t 5:00:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### PHAT
#SBATCH -A TG-AST130057
### Job name
#SBATCH -J 'fixed_dao69_miles'
### output and error logs
#SBATCH -o fixed_dao69_miles_%j.out
#SBATCH -e fixed_dao69_miles_%j.err
ibrun python-mpi prospectr.py --param_file=dao69_fixed.sh --outfile=results/fixed_dao69_miles_$SLURM_JOB_ID --nwalkers=256 --niter=1028
