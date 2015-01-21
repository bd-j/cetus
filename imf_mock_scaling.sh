#!/bin/bash
### Requested number of nodes
#SBATCH -n 16
### Requested computing time in minutes
#SBATCH -t 01:30:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Account
### imf
### PHAT
#SBATCH -A TG-AST140054

### Job name
#SBATCH -J 'imf_scaling'
### output and error logs
#SBATCH -o imf_scaling%j.out
#SBATCH -e imf_scaling%j.err
/usr/bin/time -p ibrun python-mpi prospectr.py --param_file=parfiles/imf_mock_scaling_params.py --nwalkers=30 --outfile=results/imf_scaling_nc$SLURM_NTASKS --niter=512
