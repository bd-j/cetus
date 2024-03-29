#!/usr/bin/env python
import sys, getopt, os, time
total_start = time.time()
import numpy as np
import george
from george.kernels import ExpSquaredKernel, WhiteKernel
from bsfh import sps_basis
import fsps
from sedpy.attenuation import cardelli

#sps = fsps.StellarPopulation(add_agb_dust_model=True)
#wave = sps.wavelengths
#sigma = np.random.uniform(size=len(wave))

sps = sps_basis.StellarPopBasis(smooth_velocity=False)
wave = sps.ssp.wavelengths
sigma = np.random.uniform(size=len(wave))

try:
    nw = int(sys.argv[2])
except(IndexError):
    nw = -1

ww, ss = wave[0:nw], sigma[0:nw]

def test(args):
    #start =time.time()
    arg  = args[0]
    #gaproc = args[1]
    a, s, l = 0.1, 0.0, 100.0*np.random.uniform(0,1)#arg**(0.5) + 10
    kernel = a**2 * ExpSquaredKernel(l**2) + WhiteKernel(s**2)
    gp = george.GP(kernel, solver=george.HODLRSolver)
    tinv = time.time()
    gp.compute(ww, ss)
    tinv = time.time() - tinv
    mass = getmass(arg**(0.5)/5.+0.1)
    return (os.getpid(), arg*arg, time.time()-start,
            tinv, l, mass)

def getmass(tage):
    #wave, spec = sps.get_spectrum(tage=tage, zmet =
    #                              np.fix(np.random.uniform(0,4)).astype(int)+1)
    #return sps.stellar_mass
    params = {'tage':tage, 'mass':1.0, 'dust_curve': cardelli,
              'zmet': 0.0}#np.random.uniform(-1.5,0.2)}
    spec, phot, mass = sps.get_spectrum(outwave = None, filters = None, **params)    
    return mass

start = time.time()

try:
    from emcee.utils import MPIPool
    pool = MPIPool(debug = True, loadbalance=True)
    M = pool.map
    ncpu = pool.size
    if not pool.is_master():
        # Wait for instructions from the master process.
        pool.wait()
        sys.exit(0)
except (ImportError, ValueError):
    pool = None
    M = map
    print('Not using MPI')
    ncpu = 1
    
if __name__ == '__main__':
    try:
        niter = int(sys.argv[1])
    except(IndexError):
        niter = 64
    rp = { 'outfile':'test_george_{:.0f}.dat'.format(total_start)}
    ts = time.time() - total_start
    
    j = list(M(test, [[i] for i in range(niter)]))

    fn = open(rp['outfile'],'wb')
    fn.write('# nw={0}, niter={1}, np={2}\n'.format( len(ww), niter, ncpu))
    fn.write('# initial time = {}\n'.format(ts))
    fn.write('# pid, tid^2, tproc, tinv, length, mstar\n')
    for i in j:
        fn.write('{0} {1} {2} {3} {4} {5}\n'.format(*i))
    fn.write('# total_time={}'.format(time.time() - total_start))
    fn.close()
    try:
        pool.close()
    except:
        pass
    print(time.time() - total_start)
