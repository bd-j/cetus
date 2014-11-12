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
    a, s, l = 0.1, 0.0, 100.0*np.random.uniform(0,1)#arg**(0.5) + 10
    tinv = time.time()
    gaproc.factor(s,a,l, check_finite=False)
    gaproc.factorized_Sigma = None
    tinv = time.time() - tinv 
    mass = getmass(arg**(0.5)/5.+0.1)
    return (os.getpid(), arg*arg, time.time()-start, tinv, mass)

def getmass(tage):
    #wave, spec = sps.get_spectrum(tage=tage, zmet =
    #                              np.fix(np.random.uniform(0,4)).astype(int)+1)
    #return sps.stellar_mass
    params = {'tage':tage, 'mass':1.0, 'dust_curve': cardelli,
              'zmet': np.random.uniform(-1.5,0.2)}
    spec, phot, mass = sps.get_spectrum(outwave = None, filters = None, **params)    
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

    total_start = time.time()
    rp = { 'outfile':'test_mpi_{:.0f}.dat'.format(total_start)}
    gap = gp.GaussianProcess(wave, sigma)
    a, s, l = 0.1, 0.0, 0.1
    gap.factor(s, a, l)
    gap.factorized_Sigma=None
    ts = time.time() - total_start
    
    j = list(M(test, [[i, gap] for i in range(64)]))

    fn = open(rp['outfile'],'wb')
    fn.write('initial time = {}\n'.format(ts))
    for i in j:
        fn.write('{0} {1} {2} {3} {4}\n'.format(*i))
    fn.write('total_time={}'.format(time.time() - total_start))
    fn.close()
    try:
        pool.close()
    except:
        pass
    print(time.time() - total_start)
