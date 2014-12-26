#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 64
### Requested computing time in minutes
#SBATCH -t 10:00:00
###partition
#SBATCH -p normal
### memory per cpu, in MB

### Job name
#SBATCH -J 'imf_mock'
### output and error logs
#SBATCH -o imfmock_losn_long_%j.out
#SBATCH -e imfmock_losn_long_%j.err
ibrun python-mpi prospectr.py --param_file=parfiles/imf_young_mock_params.py --nwalkers=126
