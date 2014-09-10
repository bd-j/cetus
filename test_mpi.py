####!/usr/local/bin/python
#!/opt/python/bin/python
#mpirun -np 4 python test_mpi.py > logmp

import sys, getopt, os, time
import numpy as np
from bsfh import gp
import sedpy
import fsps

try:
    import astropy.io.fits as pyfits
except(ImportError):
    import pyfits

sps = fsps.StellarPopulation(add_agb_dust_model = True)
wave = sps.wavelengths
sigma = np.random.uniform(size =len(wave))
#gap = gp.GaussianProcess(wave, sigma)

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

try:
    from emcee.utils import MPIPool
    pool = MPIPool(debug = True)
    M = pool.map
    if not pool.is_master():
        # Wait for instructions from the master process.
        pool.wait()
        sys.exit(0)
   
except ImportError:
    pool = None
    M = map

if __name__ == "__main__":

    rp = { 'outfile':'test_mpi.dat'}
    
    gap = gp.GaussianProcess(wave, sigma)
    a, s, l = 0.1, 0.0, 0.1
    gap.factor(s, a, l)
    #M = map

    j = list(M(test, [[i, gap] for i in range(60)]))

    fn = open(rp['outfile'],'wb')
    for i in j:
        fn.write('{0} {1} {2} {3}\n'.format(*i))
    fn.close()
    pool.close()
