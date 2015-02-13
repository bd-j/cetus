#Example hrdspy usage.  determine dispersion in integrated spectrum
#as a function of wavelength for a given mass and age.

import matplotlib.pyplot as pl
import time
import numpy as np
import starmodel, isochrone, cluster
from sedpy import observate, attenuation
from bsfh.readspec import load_obs_mmt

# choose a few filters and load them

# instantiate and load the isochrones and spectra first so you
# don't have to do it for each cluster realization
isoc=isochrone.Padova2007()
isoc.load_all_isoc()
speclib = starmodel.BaSeL3()
speclib.read_all_Z()

# set cluster parameters
#obsinfo =  {'objname': 'DAO69',
#            'filename':'/Users/bjohnson/Projects/cetus/data/mmt/nocal/223.DAO69.s.fits',
#            'phottable':'/Users/bjohnson/Projects/cetus/data/apdata-cluster_6phot_v4.fits',
#            'crosstable': '/Users/bjohnson/Projects/cetus/data/f2_apmatch_known.fits'}
#Z = 0.0190   #solar metallicity
#mtot = 5e3   #solar masses
#logage = 7.4   #20 Myr
#nreal = 10   #10 realizations of the cluster
#A_v = 0.9
obsinfo =  {'objname': 'B216-G267',
            'filename':'/Users/bjohnson/Projects/cetus/data/mmt/nocal/129.B216-G267.s.fits',
            'phottable':'/Users/bjohnson/Projects/cetus/data/apdata-cluster_6phot_v4.fits',
            'crosstable': '/Users/bjohnson/Projects/cetus/data/f2_apmatch_known.fits'}
Z = 0.0190   #solar metallicity
mtot = 1e4   #solar masses
logage = 8.1   #20 Myr
nreal = 10   #10 realizations of the cluster
A_v = 0.65

dm = 24.47

objname = obsinfo['objname'].lower()
obs = load_obs_mmt(**obsinfo)
phat_filterlist = obs['filters']
fwave = np.array([f.wave_effective for f in phat_filterlist])
ffreq = 2.998e18/fwave

regenerate = True
start = time.time()
if regenerate:
    # set up output
    wave = speclib.wavelength
    spectrum = np.zeros([nreal,wave.shape[0]])
    cluster_values = np.zeros([nreal, 3])

    for i in xrange(nreal):

        #use Padova2007, BaSeL3.1, and Salpeter IMF (default)
        cl = cluster.Cluster(mtot, logage, Z, isoc = isoc, speclib = speclib, IMF = None)
        cl.generate_stars()
        cl.observe_stars( phat_filterlist )
        spectrum[i,:] = cl.integrated_spectrum
        cluster_values[i,0] = cl.total_mass_formed
        cluster_values[i,1] = cl.nstars
        cluster_values[i,2] = cl.ndead

        #cl.reset_stars()
        #cl.decompose()

    s = time.time() - start
    print("Done %i clusters in %f seconds" %(nreal,s))
    
    start = time.time()
    bigcl = cluster.Cluster(mtot*nreal, logage, Z,
                            isoc = isoc, speclib = speclib, IMF = None)
    bigcl.generate_stars()
    bigcl.observe_stars( phat_filterlist )
    s = time.time() -start
    print("Done big cluster in %f seconds" %(s))

att = np.exp(-attenuation.cardelli(wave, A_v/1.086))
sed = 10**(-0.4 * (dm + observate.getSED(wave, spectrum * att[None,:],
                                   phat_filterlist)))
mean_sed = 10**(-0.4 * (dm + observate.getSED(wave, spectrum.mean(axis = 0) * att,
                                        phat_filterlist)))
big_sed = 10**(-0.4 * (dm + observate.getSED(wave, bigcl.integrated_spectrum * att / nreal,
                                       phat_filterlist)))

sfig, sax = pl.subplots() #for spectra
pfig, pax = pl.subplots() # for photometry
rfig, rax = pl.subplots() #for spectral residuals

for i in range(nreal):
    sax.plot(wave,spectrum[i,:] * att,
             alpha = 0.3, color='grey')
    pax.plot(fwave, ffreq * sed[i,:], #/sed[i,2],
             marker='o', alpha=0.4, color='green')
    rax.plot(wave, spectrum[i,:]/sed[i,2] /
             (bigcl.integrated_spectrum / big_sed[2]/nreal),
             alpha=0.4, color='grey')

sax.plot(wave, spectrum.mean(axis = 0) * att,
         color='black', linewidth=2.0,
         label =r'$\langle f_\lambda\rangle$, M$_*=${0:3.0e}'.format(mtot))
pax.plot(fwave, ffreq * mean_sed,# / mean_sed[2] ,
         color='black', linewidth=2.0, marker='o',
         label =r'$\langle \nu f_\nu\rangle$, M$_*=${0:3.0e}'.format(mtot))
sax.plot(wave, bigcl.integrated_spectrum / nreal * att,
         color='red',
         label = r'$f_\lambda/{0}$, M$_*=${1:3.0e}'.format(nreal, (mtot*nreal)) )
pax.plot(fwave, ffreq * big_sed,#/big_sed[2],
         color='red', marker='o',
         label = r'$\nu f_\nu/{0}$, M$_*=${1:3.0e}'.format(nreal, (mtot*nreal)) )
pax.errorbar(fwave, ffreq * obs['maggies'],
             ffreq * obs['maggies_unc'],
             color='blue', linewidth=2.0, marker='o',
             label = 'observed')

[ax.set_xlim(2e3,1.6e4) for ax in [sax, pax, rax]]
[ax.set_xlabel(r'$\lambda(\AA)$') for ax in [sax, pax, rax]]

#sax.set_xscale('log')
sax.set_ylim(1e-8,1e-4)
sax.set_yscale('log')
sax.set_ylabel(r'$erg/s/cm^2/\AA$ at $10pc$')
sax.legend(loc=0)
sax.set_title(r'$\log Age = {0:4.2f}$'.format(logage))
pax.legend(loc=0)
pax.set_ylabel(r'$\nu L_\nu$')
rax.set_ylabel(r'$F_\lambda$ (stochastic draw / mean)')
#pl.savefig('example4.png')
#pl.close()
sfig.show()
pfig.show()
rfig.show()
sfig.savefig('{}_stochastic_spectrum.png'.format(objname))
pfig.savefig('{}_stochastic_sed.png'.format(objname))
rfig.savefig('{}_stochastic_spec_residual.png'.format(objname))

  
    
