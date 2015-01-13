#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 128
### Requested computing time in minutes
#SBATCH -t 10:00:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### imf
#SBATCH -A TG-AST140054
### PHAT

### Job name
#SBATCH -J 'imf_dmock_morewalkers'
### output and error logs
#SBATCH -o imf_dmock_nolines_wpoly_dpoly_mwk_%j.out
#SBATCH -e imf_dmock_nolines_wpoly_dpoly_mwk_%j.err
ibrun python-mpi prospectr.py --param_file=parfiles/imf_dmock_params.py --nwalkers=254 --niter=4096
