#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 64
### Requested computing time in minutes
#SBATCH -t 15:00:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### imf
#SBATCH -A TG-AST140054
### PHAT

### Job name
#SBATCH -J 'imf_dmock'
### output and error logs
#SBATCH -o imf_dmock_nolines_wpolygp_%j.out
#SBATCH -e imf_dmock_nolines_wpolygp_%j.err
ibrun python-mpi prospectr.py --param_file=parfiles/imf_dmock_params.py --nwalkers=126
