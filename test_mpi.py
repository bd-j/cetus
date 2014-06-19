#!/usr/local/bin/python
#####!/opt/python/bin/python
#mpirun -np 4 python test_mpi.py > logmp

import sys, getopt, os, time
import numpy as np
from emcee.utils import MPIPool
import gp
import fsps

sps = fsps.StellarPopulation(add_agb_dust_model = True)
wave = sps.wavelengths
sigma = np.random.uniform(size =len(wave))

rp = { 'outfile':'test_mpi.dat'}

def test(args):
    arg  = args[0]
    gaproc = args[1]
    a, s, l = 0.1, 0.0, 0.1#arg**(0.5) + 10
    gaproc.factor(s,a,l)
    mass = test2(arg**(0.5)/5.+0.1, sps = sps)
    return (os.getpid(), arg*arg, time.time() -start, mass)

def test2(tage, sps =None):
    wave, spec= sps.get_spectrum(tage = tage)
    return sps.stellar_mass

start = time.time()

if __name__ == "__main__":

    pool = MPIPool(debug = True)
    print(pool.rank, pool.size)
    if not pool.is_master():
        # Wait for instructions from the master process.
        pool.wait()
        sys.exit(0)
 

    gap = gp.GaussianProcess(wave, sigma)
    M = pool.map
    #M = map

    j = list(M(test, [[i, gap] for i in range(32)]))
    pool.close()

    fn = open(rp['outfile'],'wb')
    for i in j:
        fn.write('{0} {1} {2} {3}\n'.format(*i))
    fn.close()
