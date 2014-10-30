#!/bin/bash
### Name of the job 
### Requested number of nodes
#SBATCH -n 32
### Requested computing time in minutes
#SBATCH -t 30
### Partition or queue name
#SBATCH -p conroy
### memory per cpu, in MB
#SBATCH --mem-per-cpu=1000
### output and error logs
#SBATCH -o mpitest.out
#SBATCH -e mpitest.err
### source activate pympi
mpirun -n 32 python test_mpi.py
