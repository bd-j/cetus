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
#SBATCH -J 'mock_imf_dao69_ckc'
### output and error logs
#SBATCH -o mock_imf_dao69_ckc_%j.out
#SBATCH -e mock_imf_dao69_ckc_%j.err
ibrun python-mpi prospectr.py --param_file=parfiles/imf_dao69_mock_params.py --outfile=results/dao69_ckc_mock_$SLURM_JOB_ID --nwalkers=510 --niter=4096
