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
#SBATCH -J 'imf_dmock_wiggle'
### output and error logs
#SBATCH -o imf_dmock_nolines_wpoly_dpoly_mwk_%j.out
#SBATCH -e imf_dmock_nolines_wpoly_dpoly_mwk_%j.err
ibrun python-mpi prospectr.py --param_file=parfiles/imf_dmock_params.py --nwalkers=510 --niter=8192
