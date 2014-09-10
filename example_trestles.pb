#!/bin/bash
# the queue to be used.
#PBS -q normal
# specify your project allocation
#PBS -A csc107
# number of nodes and number of processors per node requested
#PBS -l nodes=2:ppn=32
# requested Wall-clock time.
#PBS -l walltime=00:10:00
# name of the standard out file to be "output-file".
#PBS -o test_job_output
# name of the job
#PBS -N cetus_mpi_test 
#PBS -V
cd $PBS_O_WORKDIR #change to the working directory
module purge
module load intel mvapich2_ib
module load python
module load scipy
module load mpi4py

mpirun_rsh -np 64 -hostfile $PBS_NODEFILE test_mpi.py
