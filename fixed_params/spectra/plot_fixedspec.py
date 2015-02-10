import pickle
import numpy as np
import matplotlib.pyplot as pl

dckc = pickle.load(open('fixed_spectra_ckc.p'))
dmiles = pickle.load(open('fixed_spectra_miles.p'))
dbasel = pickle.load(open('fixed_spectra_basel.p'))
dckc2 = pickle.load(open('fixed_spectra_ckc_hs.p'))
for ckc, miles, basel, ckc2 in zip(dckc, dmiles, dbasel, dckc2):
    pl.figure()
    obs = np.exp(ckc[0]['spectrum'])
    l5500 = np.argmin(np.abs(ckc[0]['wavelength'] - 5500))
    obsnorm = ckc[1][l5500]/obs[l5500]
    pl.plot(basel[0]['wavelength'], obs * obsnorm,
            label= 'Obs (normalized to ckc at 5500AA', color='grey')

    pl.plot(ckc[0]['wavelength'], ckc[1], label='CKC', color='blue')
    pl.plot(miles[0]['wavelength'], miles[1], label='MILES', color='green')
    pl.plot(basel[0]['wavelength'], basel[1], label='BaSeL', color='red')
    pl.plot(ckc2[0]['wavelength'], ckc2[1], label='CKC lores', color='magenta')
    pl.legend(loc=0)
    print(ckc[-1].split('_')[1])
    print('----------')
    print(ckc[0]['maggies']/ckc[2])
    print(ckc2[0]['maggies']/ckc2[2])
    print(ckc[2]/ckc2[2])
    print(miles[0]['maggies']/miles[2])
    print(miles[2]/ckc2[2])
    pl.title(ckc[-1].split('_')[1])
    pl.show()
