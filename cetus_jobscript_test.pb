#!/bin/bash
# the queue to be used.
#PBS -q normal
# specify your project allocation
#PBS -A csc107
# number of nodes and number of processors per node requested
#PBS -l nodes=2:ppn=32
# requested Wall-clock time.
#PBS -l walltime=05:00:00
# name of the standard out file to be "output-file".
#PBS -o test_job_output
# name of the job
#PBS -N cetus_mpi_test 
#PBS -V
cd $PBS_O_WORKDIR #change to the working directory
mpirun_rsh -np 64 -hostfile $PBS_NODEFILE python clusters.py --param_file parfiles/b192-g242.225.cal.bpars_testing.json
