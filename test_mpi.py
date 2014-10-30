#!/usr/bin/env python
import sys, getopt, os, time
import numpy as np
from bsfh import gp, sps_basis
import fsps
from sedpy.attenuation import cardelli

#sps = fsps.StellarPopulation(add_agb_dust_model=True)
#wave = sps.wavelengths
#sigma = np.random.uniform(size=len(wave))

sps = sps_basis.StellarPopBasis(smooth_velocity=False)
wave = sps.ssp.wavelengths
sigma = np.random.uniform(size=len(wave))

#gap = gp.GaussianProcess(wave, sigma)

def test(args):
    #start =time.time()
    arg  = args[0]
    gaproc = args[1]
    a, s, l = 0.1, 0.0, 0.1*np.random.uniform(0,1)#arg**(0.5) + 10
    gaproc.factor(s,a,l)
    mass = getmass(arg**(0.5)/5.+0.1)
    return (os.getpid(), arg*arg, time.time()-start, mass)

def getmass(tage):
    #wave, spec = sps.get_spectrum(tage=tage, zmet =
    #                              np.fix(np.random.uniform(0,4)).astype(int)+1)
    #return sps.stellar_mass
    params = {'tage':tage, 'mass':1.0, 'dust_curve': cardelli,
              'zmet':np.fix(np.random.uniform(0,4)).astype(int)+1}
    spec, phot, mass = sps.get_spectrum(params, None, None)    
    return mass

start = time.time()

try:
    from emcee.utils import MPIPool
    pool = MPIPool(debug = True)
    M = pool.map
    if not pool.is_master():
        # Wait for instructions from the master process.
        pool.wait()
        sys.exit(0)
except (ImportError, ValueError):
    pool = None
    M = map
    print('Not using MPI')
   
if __name__ == '__main__': 
    rp = { 'outfile':'test_mpi.dat'}

    total_start = time.time()
    gap = gp.GaussianProcess(wave, sigma)
    a, s, l = 0.1, 0.0, 0.1
    gap.factor(s, a, l)
    gap.factorized_Sigma=None

    j = list(M(test, [[i, gap] for i in range(64)]))

    fn = open(rp['outfile'],'wb')
    for i in j:
        fn.write('{0} {1} {2} {3}\n'.format(*i))
    fn.close()
    try:
        pool.close()
    except:
        pass
    print(time.time() - total_start)
