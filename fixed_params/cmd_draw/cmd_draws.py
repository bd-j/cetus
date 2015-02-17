import numpy as np
import os
from copy import deepcopy
import matplotlib.pyplot as pl

from bsfh.gp import GaussianProcess
from bsfh import model_setup, sps_basis, readspec
from bsfh.datautils import norm_spectrum
sps = sps_basis.StellarPopBasis(compute_vega_mags=False)
nw = len(sps.ssp.wavelengths)
if nw > 6e3:
    grid = 'ckc'
elif nw > 3e3:
    grid = 'miles'
else:
    grid = 'basel'
gp = GaussianProcess(None, None)

run_params = {'param_file': '../imf_b216g267_fixedparams.py',
              #'param_file': '../imf_dao69_fixedparams.py',
              'nsample': 15,
              'objname': 'B216',
              'filename':'/work/03291/bdj314/code/cetus/data/mmt/nocal/129.B216-G267.s.fits',
              #'objname': 'DAO69',
              #'filename':'/work/03291/bdj314/code/cetus/data/mmt/nocal/223.DAO69.s.fits',
              'phottable':'/work/03291/bdj314/code/cetus/data/apdata-cluster_6phot_v4.fits',
              'crosstable': '/work/03291/bdj314/code/cetus/data/f2_apmatch_known.fits',
              'cmd_likelihood_file': '/work/03291/bdj314/code/cetus/fixed_params/cmd_draw/cmd_likelihood/ap52.all'
              #'cmd_likelihood_file': '/work/03291/bdj314/code/cetus/fixed_params/spectra/cmd_likelihood/ap94.all'
              
    }
if 'bjohnson' in os.getenv('HOME'):
    for k, v in run_params.iteritems():
        if type(v) is str:
            run_params[k] = v.replace('work/03291/bdj314/code','Users/bjohnson/Projects')

def cmd_likelihood(cmdfile):
    cols = [('av',    lambda x: x,        'dust2'),
            ('gamma', lambda x: x+1,      'imf3'),
            ('dmod',  lambda x: x,        'dmod'),
            ('logt',  lambda x: 10**x/1e9,'tage'),
            ('logz',  lambda x: x,        'zmet'),
            ('chisq', lambda x: -0.5*x,   'lnp'),
            ('sfr',   lambda x: x,        'sfr'),
            ('bg1',   lambda x: x,        'bg1'),
            ('bg2',   lambda x: x,        'bg2')
            ]
    dt = np.dtype(zip([c[2] for c in cols], len(cols) * ['<f8']))
    dat = np.loadtxt(cmdfile, dtype=dt)
    for (n1, func, n2)  in cols:
        dat[n2] = func(dat[n2])
    return dat

def sample_cmd_likelihood(cmdfile, nsamples, threshold=5):
    like = cmd_likelihood(cmdfile)
    val = np.zeros(nsamples, dtype=like.dtype)
    grid = {}

    like['lnp'] -= like['lnp'].max()
    like = like[like['lnp'] > (like['lnp'] - threshold)]
    #rejection sample
    for s in xrange(nsamples):
        lnp, cond = -1, 0
        while lnp < cond:
            #find a random grid point
            select = int(np.floor(np.random.uniform(0, len(like)-1)))

            #select = np.ones(len(like), dtype=bool)
            #for p in like_params:
            #    grid[p] = grid.get(p,np.unique(like[p]))
            #    randval = grid[p][)]
            #    select = select & (like[p] == randval)
            #if select.sum() == 1:
            val[s] = like[select]
            lnp, cond = like[select]['lnp'], np.log(np.random.uniform(0,1))
    return val
            
def get_fixed(param_file, free_params=None, **kwargs):

    model = model_setup.setup_model(param_file, sps=sps)

    ind = [c['name'] for c in model.config_list].index('sigma_smooth')
    model.config_list[ind]['init'] = 2.12

    for c in model.config_list:
        if c['name'] in free_params:
            c['isfree'] = True
        else:
            c['isfree'] = False
        if c['name'] in kwargs:
            c['init'] = kwargs[c['name']]
            
    model.configure()

    #mu, phot, x = model.mean_model(model.theta, sps=sps)
    return model #, mu, phot


if __name__ == "__main__":

    free_params = ['dust2', 'imf3', 'zmet', 'tage']
    model = get_fixed(run_params['param_file'],
                      free_params=free_params,
                      gp_jitter=0.0, gp_amplitude=0.0,
                      poly_coeffs=np.array([0.0,0.0]))

    obs = model.obs
    obs['spectrum'] = np.exp(obs['spectrum'])
    onorm, pwave = norm_spectrum(obs)
    mask = deepcopy(obs['mask'])
    fwave = np.array([f.wave_effective for f in obs['filters']])
    fnu = 2.998e18/fwave
    #remove the mask temporarily
    model.obs['mask'] = np.ones(len(obs['wavelength']), dtype= bool)

    val = sample_cmd_likelihood(run_params['cmd_likelihood_file'],
                                run_params['nsample'])
    thetas = val[model.theta_labels()]
    sfig, sax = pl.subplots()
    rfig, rax = pl.subplots()
    pfig, pax = pl.subplots()
    sedfig, sedax = pl.subplots()
    for theta in thetas:
        
        mu, phot, x = model.mean_model(np.array(list(theta)), sps=sps)
        tobs = deepcopy(obs)
        tobs['spectrum'] = mu
        tnorm, pwave = norm_spectrum(tobs)
        sax.plot(obs['wavelength'], mu / tnorm, color='magenta', alpha = 0.3)
        sax.plot(obs['wavelength'], obs['spectrum']/onorm, color='grey')
        rax.plot(obs['wavelength'], (mu /obs['spectrum']*onorm/ tnorm),
                 color='blue', alpha = 0.3)
        rax.plot(obs['wavelength'][mask], (mu /obs['spectrum']*onorm/ tnorm)[mask],
                 color='orange', alpha = 0.3)
        pnorm = ((phot*obs['maggies']/obs['maggies_unc']**2)[obs['phot_mask']].sum() /
                 ((phot/obs['maggies_unc'])**2)[obs['phot_mask']].sum())
        pax.plot(fwave,
                 (pnorm*phot-obs['maggies'])/obs['maggies_unc'],
                 marker='o', color='magenta', alpha = 0.3)
        sedax.plot(fwave,
                 (pnorm*phot)* fnu,
                 marker='o', color='magenta', alpha = 0.3)
    sedax.errorbar(fwave,
                   obs['maggies'] * fnu,
                   fnu * np.sqrt(obs['maggies_unc']**2 + (0.05*obs['maggies_unc'])**2),
                   marker ='o', color='black')
    rax.set_xlim(3650, 8e3)
    rax.set_ylim(0.5, 2.5)
    rax.set_ylabel('CMD model / obs')
    pax.set_ylabel(r'$(C \times SED_{{CMD model}} - SED_{{obs}})/\sigma$')
    [ax.set_title(run_params['objname']) for ax in [sax, pax, rax, sedax]]
    sedax.set_ylabel(r'$\nu f_\nu$')
    [f.savefig('{0}_{1}_{2}.png'.format(run_params['objname'].lower(), grid, ftype))
     for f, ftype in zip([sedfig, rfig, pfig], ['sed', 'specresid', 'photchi'])]
               
    pfig.show()
    sfig.show()
    rfig.show()
    sedfig.show()
    
