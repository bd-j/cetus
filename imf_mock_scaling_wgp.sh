#!/bin/bash
### Requested number of nodes
#SBATCH -n 32
### Requested computing time in minutes
#SBATCH -t 00:30:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### imf
### PHAT
#SBATCH -A TG-AST140054

### Job name
#SBATCH -J 'imf_gpscaling'
### output and error logs
#SBATCH -o imf_gpscaling%j.out
#SBATCH -e imf_gpscaling%j.err
/usr/bin/time -p ibrun python-mpi prospectr.py --param_file=parfiles/imf_mock_scaling_wgp_params.py --nwalkers=62 --outfile=results/imf_scalingwgp_nc$SLURM_NTASKS
