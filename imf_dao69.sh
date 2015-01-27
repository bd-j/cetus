#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 256
### Requested computing time in minutes
#SBATCH -t 10:00:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### PHAT
#SBATCH -A TG-AST130057
### Job name
#SBATCH -J 'imf_dao69_miles'
### output and error logs
#SBATCH -o imf_dao69_miles_%j.out
#SBATCH -e imf_dao69_miles_%j.err
ibrun python-mpi prospectr.py --param_file=parfiles/imf_dao69_params.py --nwalkers=510 --niter=8192
