#!/usr/local/bin/python

import time, sys, os
import numpy as np
import pickle

from bsfh import sps_basis, sedmodel, modeldef
from bsfh.gp import GaussianProcess
import bsfh.fitterutils as utils
import bsfh.datautils as dutils

#SPS Model as global
smooth_velocity = False
sps = sps_basis.StellarPopBasis(smooth_velocity = smooth_velocity)

#Gp as global
gp = GaussianProcess(None, None)

#LnP function as global
def lnprobfn(theta, mod):
    """
    Given a model object and a parameter vector, return the ln of the
    posterior.
    """
    lnp_prior = mod.prior_product(theta)
    if np.isfinite(lnp_prior):
        
        # Generate mean model
        t1 = time.time()        
        mu, phot, x = mod.mean_model(theta, sps = sps)
        log_mu = np.log(mu)
        #polynomial in the log
        log_cal = (mod.calibration(theta))
        mask = mod.obs['mask']
        d1 = time.time() - t1

        # Spectroscopy term
        t2 = time.time()
        gp.wave, gp.sigma = mod.obs['spectrum'][mask], mod.obs['unc'][mask]
        #use a residual in log space
        delta = (mod.obs['spectrum'] - log_mu - log_cal)[mask]
        gp.factor(mod.params['gp_jitter'], mod.params['gp_amplitude'],
                  mod.params['gp_length'], check_finite=False, force=False)
        lnp_spec = gp.lnlike(delta)
        d2 = time.time() - t2

        # Photometry term
        jitter = mod.params.get('phot_jitter',0)
        maggies = 10**(-0.4 * mod.obs['mags'])
        phot_var = maggies**2 * ((mod.obs['mags_unc']**2 + jitter**2)/1.086**2)
        lnp_phot =  -0.5*( (phot - maggies)**2 / phot_var ).sum()
        lnp_phot +=  -0.5*np.log(phot_var).sum()

        if mod.verbose:
            print(theta)
            print('model calc = {0}s, lnlike calc = {1}'.format(d1,d2))
            fstring = 'lnp = {0}, lnp_spec = {1}, lnp_phot = {2}'
            values = [lnp_spec + lnp_phot + lnp_prior, lnp_spec, lnp_phot]
            print(fstring.format(*values))
        return lnp_prior + lnp_phot + lnp_spec
    else:
        return -np.infty
    
def chisqfn(theta, mod):
    return -lnprobfn(theta, mod)

#MPI pool.  This must be done *after* lnprob and
# chi2 are defined since slaves will only see up to
# sys.exit()
try:
    from emcee.utils import MPIPool
    pool = MPIPool(debug = False, loadbalance = True)
    if not pool.is_master():
        # Wait for instructions from the master process.
        pool.wait()
        sys.exit(0)
except(ValueError):
    pool = None
    
if __name__ == "__main__":

    inpar = utils.parse_args(sys.argv)
    parset = modeldef.ProspectrParams(inpar['param_file'])
    rp = parset.run_params

    ###############
    # MODEL SET UP
    ##############
    if rp['verbose']:
        print('Setting up model')

    model, initial_center = parset.initialize_model(sedmodel.SedModel)
    #model.params['smooth_velocity'] = smooth_velocity
    parset.run_params['ndim'] = model.ndim
    
    ############
    # LOAD DATA
    ##############
    if rp['verbose']:
        print('Loading data')
    if rp.get('mock', False):
        mock = rp['mock_info']
        obs = dutils.generate_mock(model, sps, mock)
        initial_center = model.theta_from_params()
        initial_center *= np.random.beta(2,2,size=model.ndim)*2.0
    else:
        obs = dutils.load_obs_mmt(**rp)
        #ignore the IR magnitudes
        obs['mags'] = obs['mags'][0:4]
        obs['mags_unc'] = obs['mags_unc'][0:4]
        obs['filters'] = obs['filters'][0:4]
        
    modeldef.add_obs_to_model(model, obs, initial_center,
                              spec=True, phot=True,
                              logify_spectrum=True,
                              normalize_spectrum=True,
                              add_gaussian_process=False)
    
    model.params['smooth_velocity'] = smooth_velocity
      
    #################
    #INITIAL GUESS USING POWELL MINIMIZATION
    #################
    #sys.exit()
    if rp['verbose']:
        print('Minimizing')
    ts = time.time()
    powell_opt = {'ftol': rp['ftol'], 'xtol':1e-6,
                'maxfev':rp['maxfev']}
    powell_guesses, pinit = utils.pminimize(chisqfn, model, initial_center,
                                       method ='powell', opts =powell_opt,
                                       pool = pool, nthreads = rp['nthreads'])
    
    best = np.argmin([p.fun for p in powell_guesses])
    best_guess = powell_guesses[best]
    pdur = time.time() - ts
    
    if rp['verbose']:
        print('done Powell in {0}s'.format(pdur))

    ###################
    #SAMPLE
    ####################
    #sys.exit()
    if rp['verbose']:
        print('emcee...')
    tstart = time.time()
    
    #nsamplers = int(rp['nsamplers'])
    theta_init = initial_center
    initial_center = best_guess.x #np.array([8e3, 2e-2, 0.5, 0.1, 0.1, norm])
    esampler = utils.run_emcee_sampler(model, lnprobfn, initial_center, rp, pool = pool)
    edur = time.time() - tstart

    ###################
    # PICKLE OUTPUT
    ###################
    results, model_store = {}, {}
    
    results['run_params'] = rp
    results['obs'] = model.obs
    results['plist'] = parset.model_params
    results['pardict'] =  modeldef.plist_to_pdict([modeldef.functions_to_names(p)
                                                  for p in parset.model_params])
    results['initial_center'] = initial_center
    results['initial_theta'] = theta_init
    
    results['chain'] = esampler.chain
    results['lnprobability'] = esampler.lnprobability
    results['acceptance'] = esampler.acceptance_fraction
    results['duration'] = edur
    results['optimizer_duration'] = pdur

    model_store['powell'] = powell_guesses
    model_store['model'] = model
    #pull out the git hash for bsfh here.
    bsfh_dir = os.path.dirname(modeldef.__file__)
    bgh = utils.run_command('cd ' + bsfh_dir +
                           '\n git rev-parse HEAD')[1][0].replace('\n','')
    cgh = utils.run_command('git rev-parse HEAD')[1][0].replace('\n','')

    results['bsfh_version'] = bgh
    results['cetus_version'] = cgh
    model_store['bsfh_version'] = bgh
    
    tt = int(time.time())
    out = open('{1}_{0}_mcmc'.format(tt, rp['outfile']), 'wb')
    pickle.dump(results, out)
    out.close()

    out = open('{1}_{0}_model'.format(tt, rp['outfile']), 'wb')
    pickle.dump(model_store, out)
    out.close()
    
    try:
        pool.close()
    except:
        pass
