#!/bin/bash
### Name of the job 
#PBS -N cetus_test
### Requesting 4 nodes, with 15 processors per node 
#PBS -l nodes=4:ppn=15
### Requesting 10 hours of computing time
#PBS -l walltime=3:00:00
cd $PBS_O_WORKDIR
module load python
mpirun -genv I_MPI_FABRICS shm:ofa -n 60 python bsfh.py --param_file B192_cal.params