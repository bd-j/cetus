#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 32
### Requested computing time in minutes
#SBATCH -t 30
### memory per cpu, in MB
#SBATCH --mem-per-cpu=1000
### output and error logs
#SBATCH -o mpitest.out
#SBATCH -e mpitest.err
#SBATCH 
mpirun -n 32 python test_mpi.py
