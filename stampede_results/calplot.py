import sys, pickle
import numpy as np
import matplotlib.pyplot as pl
from matplotlib import gridspec

from bsfh import read_results as bread
from bsfh import sps_basis
from bsfh.gp import GaussianProcess

sps = sps_basis.StellarPopBasis()
gp = GaussianProcess(None, None)


def add_wiggles(datadir="/work/03291/bdj314/code/cetus/data/", **extras):
    from bsfh.datautils import load_obs_mmt

    pars = {'phottable':datadir + "f2_apcanfinal_6phot_v2.fits",
            'objname':'B192-G242',
            'wlo':3750., 'whi':7200.
            }
    calname = datadir + "mmt/nocal/020.B192-G242.s.fits"
    uncalname = datadir + "mmt/nocal/020.B192-G242.v.fits"
            
    cal = load_obs_mmt(filename=calname, **pars)
    uncal = load_obs_mmt(filename=uncalname, **pars)
    calibration = (uncal['spectrum']/cal['spectrum'])[cal['mask']]
    return calibration


def comp_samples(thetas, model):
    specvecs =[]
    obs = model.obs
    wave, ospec, mask = obs['wavelength'], obs['spectrum'], obs['mask']
    mwave, mospec = wave[mask], ospec[mask]
    mounc = obs['unc'][mask]
    gp.wave, gp.sigma = mwave, obs['unc'][mask]
    mospec = np.exp(mospec)
         #mounc *= mospec

    for theta in thetas:
        mu, cal, delta, mask, wave = bread.model_comp(theta, model, sps,
                                                      gp=gp, inlog=True,
                                                      photflag=0)
        cal = np.exp(cal)
        full_cal = np.exp(np.log(cal) + delta)
        mod = np.exp(mu + np.log(cal) + delta)
        mu = np.exp(mu)
            
        specvecs += [ [mu, cal, delta, mod,
                       np.exp(np.log(mospec)-np.log(mod)),
                       (np.log(mospec)-np.log(mod)) / mounc] ]
            
    return wave, mospec, mounc, specvecs

def comp_samples_phot(thetas, model):
    specvecs =[]
    obs = model.obs
    wave = np.array([f.wave_effective for f in obs['filters']])
    mospec = obs['maggies']
    mounc = obs['maggies_unc']
    mask = obs['phot_mask']
    zero = np.zeros(mask.sum())
    
    for theta in thetas:
        mu = model.mean_model(theta, sps=sps)[1][mask]
        specvecs += [ [mu, zero, zero, mu, mospec - mu, (mospec - mu)/mounc] ]
    return wave, mospec, mounc, specvecs

def theta_samples(res, samples=[1.0], start=0.0, thin=1):

    nw, niter = res['chain'].shape[:-1]
    start_index = np.floor(start * (niter-1)).astype(int)
    flatchain = res['chain'][:,start_index::thin,:]
    flatchain = flatchain.reshape(flatchain.shape[0] * flatchain.shape[1],
                                  flatchain.shape[2])
    ns = flatchain.shape[0]
    thetas = [flatchain[s,:] for s in np.floor(np.array(samples) * (ns-1)).astype(int)]
    return thetas, start_index, np.floor(np.array(samples) * (ns-1)).astype(int)
    
def calfig(wave, calvec, specvecs, norm=1.0, fax=None):
    if fax is None:
        cfig, cax = pl.subplots()
    else:
        cfig, cax = fax
    #plot the calibration vector 
    cax.plot(wave, calvec, color='black', linewidth=3.0, label='Mock Truth')
    # and posterior samples of it
    for i, specs in enumerate(specvecs):
        if i==0:
            label = 'Posterior sample'
        else:
            label = None
        cax.plot(wave, norm * np.exp(np.log(specs[1]) + specs[2]),
                 color='green', alpha = 0.3, label=label)
    
    return cfig, cax

def obsfig(wave, obsvec, specvecs, unc=None, fax=None):
    if fax is None:
        ofig, oax = pl.subplots()
    else:
        ofig, oax = fax
    #plot the observation
    if unc is not None:
        x, y, e = wave, obsvec, unc
        oax.fill_between(x, y-e, y+e, facecolor='grey', alpha=0.3)
    oax.plot(wave, obsvec, color='black', linewidth=3.0, label='Mock Observed Spectroscopy')
    # and posterior samples of it
    for i, specs in enumerate(specvecs):
        if i==0:
            label = 'Posterior samples'
        else:
            label = None
        oax.plot(wave, specs[3],
                 color='green', alpha = 0.3, label=label)
    return ofig, oax

def sedfig(wave, specvecs, phot, photvecs, norm = 1.0, fax=None):

    if fax is None:
        sfig, sax = pl.subplots()
    else:
        sfig, sax = fax
    pwave, sed, sed_unc = phot
    # to convert from f_lambda cgs/AA to lambda*f_lambda cgs
    sconv = wave * norm
    # to convert from maggies to nu * f_nu cgs
    pconv = 3631e-23 * 2.998e18/pwave

    for i, (specs, seds) in enumerate(zip(specvecs, photvecs)):
        if i==0:
            label = 'Posterior samples'
        else:
            label = None
        sax.plot(wave, specs[0] * sconv,
                 color='green', alpha=0.3, label=label)
        sax.plot(pwave, seds[0] * pconv, markersize=8.0, linestyle='',
                 marker='o', color='magenta', label=label)

    sax.errorbar(pwave, sed * pconv, yerr=sed_unc * pconv,
                 marker='o', markersize=8.0,
                 color='black', linestyle='', label='Mock Photometry')

    return sfig, sax

def hist_samples(res, model, showpars, start=0, thin=1, **kwargs):
    
    nw, niter = res['chain'].shape[:-1]
    parnames = np.array(model.theta_labels())
    start_index = np.floor(start * (niter-1)).astype(int)
    flatchain = res['chain'][:,start_index::thin,:]
    flatchain = flatchain.reshape(flatchain.shape[0] * flatchain.shape[1],
                                  flatchain.shape[2])
    ind_show = np.array([p in showpars for p in parnames], dtype= bool)
    flatchain = flatchain[:,ind_show]
    return flatchain

def histfig(samples, parnames, truths=None, fax=None, truth_color='k', **kwargs):
    npar = len(parnames)

    if fax is None:
        nx = int(np.floor(np.sqrt(npar)))
        ny = int(np.ceil(npar*1.0/nx))
        hfig, haxes = pl.subplots(nx, ny)
    else:
        hfig, haxes = fax
        
    for i, (ax, name) in enumerate(zip(haxes.flatten(), parnames)):
        ax.hist(samples[:,i], bins=kwargs.get("bins", 50),
                histtype="stepfilled",
                color=kwargs.get("color", "k"),
                alpha = 0.5,
                label = 'posterior PDF')
        if truths is not None:
            ax.axvline(truths[i], color=truth_color, label='Mock Truth')
        ax.set_xlabel(name)
        ax.set_yticklabels([])
        
    return hfig, haxes

if __name__ == "__main__":

    resfile = ('imf_dmock_snrx2_nolines_wnewpoly_polydata_1421277554_mcmc',
               'imf_dmock_snrx2_nolines_wnewpoly_polydata_1421225304_mcmc')

    calvec = add_wiggles(datadir='/Users/bjohnson/Projects/cetus/data/')

    i=0
    res, pr, mod = bread.read_pickles(resfile[i],
                                      model_file=resfile[i].replace('_mcmc','_model'))
    fsamples = np.random.uniform(0,1,10)
    thetas, start, samples = theta_samples(res, samples=fsamples, start=0.75, thin=1)
    mwave, mospec, mounc, specvecs = comp_samples(thetas, mod)
    pwave, mosed, mosed_unc, pvecs = comp_samples_phot(thetas, mod)
    
    norm = mod.params['normalization_guess'] * mod.obs['scale']

    fig = pl.figure(figsize=(10,8))
    gs1 = gridspec.GridSpec(3, 1)
    gs1.update(left=0.05, right=0.48, wspace=0.05)
    oax = pl.subplot(gs1[:-1,0])
    cax = pl.subplot(gs1[-1,0])
    
    gs2 = gridspec.GridSpec(4, 2)
    gs2.update(left=0.55, right=0.98, hspace=0.3)
    sax = pl.subplot(gs2[0:2,:])
    haxes = np.array([pl.subplot(gs2[i, j]) for i in [2,3] for j in [0,1]])

    cfig, cax = calfig(mwave, calvec, specvecs, norm=norm, fax=(None, cax))
    cax.set_ylabel(r'Calibration $F_{{obs}}/F_{{intrinsic}}$')
    cax.legend(loc=0)
    #cfig.show()
    #cfig.savefig('example_cal.png')
    
    sfig, sax = sedfig(mwave, specvecs, [pwave, mosed, mosed_unc], pvecs,
                       norm=1/mod.params['normalization_guess'], fax=(None,sax))
    sax.set_xscale('log')
    sax.set_xlim(2.5e3, 1.6e4)
    sax.legend(loc=0, prop={'size':12})
    sax.set_ylabel(r'$\lambda F_{{\lambda}}$ (intrinsic, cgs)')
    #sfig.show()
    #sfig.savefig('example_sed.png')
    
    ofig, oax = obsfig(mwave, mospec, specvecs, unc=mounc, fax=(None,oax))
    oax.set_ylabel(r'Observed Spectrum $F_{{\lambda}}$')
    oax.legend(loc=0)
    #ofig.show()
    #ofig.savefig('example_obs.png')

    pnames = ['mass', 'tage', 'dust2', 'imf3']
    samples = hist_samples(res, mod, pnames, start=0.5, thin=10)
    hfig, haxes = histfig(samples, pnames, truths = [1e4, 0.05, 0.3, 2.7],
                          color='green', fax=(None, haxes))
    haxes[0].legend(loc=0, prop={'size':8})
    
    #gs1.tight_layout(fig)
    #hfig.show()
    #hfig.savefig('example_hist.png')

    #[fig.add_axes(ax) for ax in [oax, cax, sax] + haxes.flatten()]
    #fig.show()
