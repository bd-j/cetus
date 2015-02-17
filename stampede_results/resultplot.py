import sys, pickle
import numpy as np
import matplotlib.pyplot as pl
from matplotlib import gridspec

from bsfh import read_results as bread
from bsfh.gp import GaussianProcess
from bsfh import sps_basis
sps = sps_basis.StellarPopBasis()
gp = GaussianProcess(None, None)

def comp_samples(thetas, model, inlog=True, photflag=0):
    specvecs =[]
    obs, _, marker = bread.obsdict(model.obs, photflag)
    wave, ospec, mask = obs['wavelength'], obs['spectrum'], obs['mask']
    mwave, mospec = wave[mask], ospec[mask]
    mounc = obs['unc'][mask]
    gp.wave, gp.sigma = mwave, obs['unc'][mask]
    if inlog and (photflag == 0):
        mospec = np.exp(mospec)
         #mounc *= mospec

    for theta in thetas:
        mu, cal, delta, mask, wave = bread.model_comp(theta, model, sps,
                                                      gp=gp, inlog=True,
                                                      photflag=photflag)
        cal = np.exp(cal)
        if inlog & (photflag == 0):
            full_cal = np.exp(np.log(cal) + delta)
            mod = np.exp(mu + np.log(cal) + delta)
            mu = np.exp(mu)
            
        elif photflag == 0:
            full_cal = cal + delta/mu
            mod = (mu*cal + delta)
        else:
            mod = mu

        specvecs += [ [mu, cal, delta, mod,
                       np.exp(np.log(mospec)-np.log(mod)),
                       (np.log(mospec)-np.log(mod)) / mounc] ]
            
    return wave, mospec, mounc, specvecs

def spec_figure(results, alpha=0.3, samples=[-1],
                start=0, thin=1, inlog=True,
                subplot_spec=None, xlim=None, **kwargs):
    """
    plot stars+dust+neb, then the calibration vector, then the GP
    predicitions, then data and full model, then residuals
    """
    
    fig = pl.figure(figsize = (10,6))
    gs = gridspec.GridSpec(3, 2, height_ratios=[3,1,1], hspace=0, wspace=0.05)
    
    # Axis variables
    ylabels = [r'$\mu$',r'$e^{f(\alpha)}$', r'$\tilde{\Delta}$ (GP)',
               #r'$\delta[f(\alpha)\mu]$ (GP)',
               r'$\mu \, e^{f(\alpha) + \tilde{\Delta}}$','o/m', r'$\chi$']
    color = ['blue', 'green', 'red', 'magenta', 'orange','orange']
    row = [0,1,2,0,1,2]
    col = [0,0,0,1,1,1]
    show_tick = [False, False, True, False, False, True]
    
    # Generate axes
    axes = [pl.Subplot(fig, gs[c,r]) for r,c in zip(col, row)]
    # Suppress ticks on shared axes
    [pl.setp(ax.get_xticklabels(), visible = sh) for ax,sh in zip(axes, show_tick)]
    # Y-labels
    [ax.set_ylabel(label) for ax, label in zip(axes, ylabels)]
    [pl.setp(ax.yaxis, label_position='right') for ax in axes[3:]]
    [ax.yaxis.set_ticks_position('right') for ax in axes[3:]]
    [ax.yaxis.set_ticks_position('both') for ax in axes[3:]]

    # Make posterior draws
    flatchain = results['chain'][:,start::thin,:]
    flatchain = flatchain.reshape(flatchain.shape[0] * flatchain.shape[1],
                                  flatchain.shape[2])
    thetas = [flatchain[s,:] for s in samples]
    thetas += [results['sampling_initial_center']]

    mwave, mospec, mounc, specvecs = comp_samples(thetas, results['model'], inlog=inlog)
    
    # Plot the data
    axes[3].plot(mwave, mospec, color='grey', label='Obs', **kwargs)
    # Plot posterior draws
    print(len(specvecs), len(axes), len(color))
    for vecs in specvecs[:-1]:
        [ax.plot(mwave, v, color=c, alpha=alpha, **kwargs)
         for ax,v,c in zip(axes, vecs, color)]
    # Plot the minimizer result
    #[ax.plot(mwave, v, color='cyan', alpha=1.0, **kwargs)
    # for ax,v in zip(axes, specvecs[-1])]

    [a.axhline( int(i==0), linestyle=':', color='black')
     for i,a in enumerate(axes[-2:])]
    if xlim is not None:
        [a.set_xlim(xlim) for a in axes]
    # Add axes to the figure
    [fig.add_subplot(ax) for ax in axes]
    return fig

def phot_figure(results, alpha=0.3, samples = [-1],
                start=0, thin=1,
                **kwargs):
    """
    Plot the photometry for the model and data (with error bars). Then
    plot residuals
    """
    fig = pl.figure()
    gs = gridspec.GridSpec(2,1, height_ratios=[3,1])
    gs.update(hspace=0)
    phot, res = pl.Subplot(fig, gs[0]), pl.Subplot(fig, gs[1])
    res.set_ylabel( r'$\chi$')
    phot.set_ylabel('maggies')
    
    # posterior draws
    flatchain = results['chain'][:,start::thin,:]
    flatchain = flatchain.reshape(flatchain.shape[0] * flatchain.shape[1],
                                  flatchain.shape[2])
    thetas = [flatchain[s,:] for s in samples]
    mwave, mospec, mounc, specvecs = comp_samples(thetas, results['model'], photflag=1)
    #print(mwave, mospec)
    for vecs in specvecs:
        vv = vecs[0], (vecs[3] - mospec)/mounc
        [ax.plot(mwave, v, color='magenta', alpha=alpha, marker='o', **kwargs)
         for ax, v in zip([phot, res], vv) ]
    
    phot.errorbar(mwave, mospec, yerr=mounc,
                  color='black')
    phot.plot(mwave, mospec, label = 'observed',
              color='black', marker='o', **kwargs)
    phot.legend(loc=0)
    res.axhline(0, linestyle=':', color='grey')
    
    fig.add_subplot(phot)
    fig.add_subplot(res)
    
    return fig

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


if __name__ == '__main__':


    sflist = [#'dao69_ckc_lowsn_4835362_1423452691_mcmc',
              'dao69_ckc_mock_4846825_1423747216_mcmc',
              #'b216g267_ckc_4816596_1423124523_mcmc',
              #'dao69_ckc_4816598_1423124059_mcmc'
              #'ap244_miles_4781921_1422547421_mcmc',
              #'ap552_miles_4781922_1422546888_mcmc',
              #'b216g267_miles_4781920_1422543238_mcmc',
              #'dao69_miles_4777077_1422446987_mcmc'
              ]
        
    showpars_phys = ['mass', 'tage', 'zmet', 'dust2', 'imf3', 'zred', 'sigma_smooth',
                    'spec_norm', 'poly_coeffs1', 'poly_coeffs2',
                    'gp_jitter', 'gp_amplitude', 'gp_length']
    showpars_cal = ['imf3','poly_coeffs1', 'poly_coeffs2',
                    'gp_length', 'gp_amplitude', 'gp_jitter']

    nsample = 5
    samples = np.random.uniform(0, 1, size=nsample)
    zoom_regions = [[3750,4100.], [6500, 6600.], [5850, 5950], [5000, 5400]]

    for sf in sflist:
        result, pr, model = bread.read_pickles(sf, model_file=sf.replace('_mcmc','_model'))
        ns = result['chain'].shape[0] * result['chain'].shape[1]
        sample = [int(s * ns) for s in samples]
    
        sfig = spec_figure(result, samples=sample, inlog=True,
                           linewidth = 0.5, xlim = (3650, 7300))

        sfig.show()
        sfig.savefig(sf.replace('_mcmc','.spec.png'))
            
        #sys.exit()
        efig = bread.param_evol(result, showpars =showpars_phys)
        efig.savefig(sf.replace('_mcmc','.pevol.png'))
        pl.close(efig)
        tfig = bread.subtriangle(result, showpars = showpars_phys,
                                 start=int(result['chain'].shape[1]/2.), thin=10)
        tfig.savefig(sf.replace('_mcmc','.corner.png'))
        pl.close(tfig)
        pfig = phot_figure(result, samples=sample)
        pfig.savefig(sf.replace('_mcmc','.sed.png'))
        pfig.show()
