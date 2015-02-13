import numpy as np
import fsps

# set cluster parameters
Z = 0.0190   #solar metallicity
mtot = 5e3   #solar masses
logage = 7.4   #20 Myr
A_v = 0.9

sps = fsps.StellarPopulation(compute_vega_mags=True, zoncontinuous=0)
sps.params['sfh'] = 0
sps.params['imf'] = 0
sps.params['tage'] = 10**logage/1e9
zind =np.argmin(np.abs(sps.zlegend - Z))
sps.params['zmet'] = zind+1

w, s = sps.get_spectrum(tage=sps.params['tage'], zmet=sps.params['zmet'])
dat = sps.isochrones()
isoc = dat[dat['age'] == logage]

masses = isoc['mass']
weights = mtot * 10**isoc['log(weight)']
mhist, medges = np.histogram(masses, weights = weights, bins=np.arange(0.08, 100, 0.1))

bands = (['wfc3_uvis_'+b.lower() for b in ["F336W", "F475W", "F814W"]] +
                  ['wfc3_ir_'+b.lower() for b in ["F110W", "F160W"]])
params = ['mass', 'logl', 'logt'] + bands
grids = {}
for p in params:
    grids[p] = np.linspace(np.min(isoc[p]), np.max(isoc[p]), 20)

x = 'logl'
y = 'logt'
hess, xbin, ybin = np.histogram2d(isoc[x], isoc[y],
                                  bins=(grids[x], grids[y]),
                                  weights=weights)
stoch = (hess < 2) & (hess > 0)
pl.imshow(hess, interpolation='nearest',origin='lower')
pl.xlim(len(xbin)-1.5,-0.5)
pl.colorbar()
