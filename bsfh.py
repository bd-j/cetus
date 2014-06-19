#!/usr/local/bin/python

import time, sys, os
import numpy as np
import pickle

import sps_basis
import bsfh_model
import bsfh_utils as utils

#SPS Model as global
sps = sps_basis.StellarPopBasis(smooth_velocity = fixed_params['smooth_velocity'])

#LnP function as global
def lnprobfn(theta, mod):
    """
    Wrapper on the model instance method, defined here
    globally to enable multiprocessing.
    """
    lnp_prior = mod.prior_product(theta)
    if np.isfinite(lnp_prior):
        print(theta)
        
        # Generate model
        t1 = time.time()        
        spec, phot, x = mod.model(theta, sps = sps)
        d1 = time.time() - t1

        # Spectroscopy term
        t2 = time.time()
        r = (mod.obs['spectrum'] - spec)[mod.obs['mask']]
        mod.gp.factor(mod.params['gp_jitter'], mod.params['gp_amplitude'],
                      mod.params['gp_length'], check_finite = False)
        lnp_spec = mod.gp.lnlike(r)
        d2 = time.time() - t2

        # Photometry term
        jitter = mod.params.get('phot_jitter',0)
        maggies = 10**(-0.4 * mod.obs['mags'])
        phot_var = maggies**2 * ((mod.obs['mags_unc']/1.086)**2 + jitter**2)
        lnp_phot =  -0.5*( (phot - maggies)**2 / phot_var ).sum()
        lnp_phot +=  np.log(2*np.pi*phot_var).sum()

        print('model calc = {0}s, lnlike calc = {1}'.format(d1,d2))
        print('lnp = {0}, lnp_spec = {1}, lnp_phot = {2}'.format(lnp_spec + lnp_phot + lnp_prior, lnp_spec, lnp_phot))
        return lnp_prior + lnp_phot + lnp_spec
    else:
        return -np.infty
    
def chi2(args):
    """
    A sort of chi2 function that allows for maximization of lnP using
    minimization routines.
    """
    theta, model = args
    return -lnprobfn(theta, model)

# Run parameters
rp = {'verbose':True,
      #data
      'filename':'data/mmt/nocal/020.B192-G242.s.fits', 'objname': 'B192-G242',
      'wlo':3750., 'whi': 7200.,
      'loader': 'load_obs_mmt',
      #model
      'param_file':'bsfh.params',
      #for minimization
      'ftol':1e-6, 'maxfev':50000, 'nsamplers':1,
      #for emcee sampling
      'walker_factor':8,'nthreads':1, 'nburn':3 * [50], 'niter': 200, 'initial_disp':0.01
      #for MPI
      'np':1
      }

fc = os.path.basename(rp['filename']).split('.')
rp['outfile'] = 'results/' + 'test_{0}{2}_{1}'.format(fc[1].lower(), fc[0], fc[2]) 


if __name__ == "__main__":

    rp = utils.parse_args(sys.argv,rp)

    ############
    # LOAD DATA
    ##############
    if rp['verbose']:
        print('Loading data')

    obs = utils.load_obs_mmt(**rp)
    #ignore the IR magnitudes
    obs['mags'] = obs['mags'][0:4]
    obs['mags_unc'] = obs['mags_unc'][0:4]
    obs['filters'] = obs['filters'][0:4]

    ###############
    #MODEL SET UP
    ##############
    if rp['verbose']:
        print('Setting up model')

    model, initial_center = bsfh_model.initialize_model(rp, obs)

    #################
    #INITIAL GUESS USING POWELL MINIMIZATION
    #################
    #sys.exit()
    if rp['verbose']:
        print('Minimizing')

    powell_opt = {'ftol': rp['ftol'],
                  'xtol':1e-6,
                  'maxfev':rp['maxfev']}
    powell_guesses, pinit = utils.parallel_minimize(model, sps, chi2, initial_center, rp, powell_opt, pool = pool)
    best = np.argmin([p.fun for p in powell_guesses])
    powell_guess = powell_guesses[best]

    ###################
    #SAMPLE
    ####################
    #sys.exit()
    if rp['verbose']:
        print('emcee...')

    nsamplers = int(rp['nsamplers'])

    tstart = time.time()
    theta_init = initial_center
    initial_center = powell_guess.x #np.array([8e3, 2e-2, 0.5, 0.1, 0.1, norm])
    esampler = utils.run_a_sampler(model, sps, lnprobfn, initial_center, rp, pool = pool)
    edur = time.time() - tstart

    ###################
    # PICKLE OUTPUT
    ###################
    results = {}
    results['run_params'] = rp
    results['obs'] = model.obs
    results['theta'] = model.theta_desc
    results['initial_center'] = initial_center
    results['chain'] = esampler.chain
    results['lnprobability'] = esampler.lnprobability
    results['acceptance'] = esampler.acceptance_fraction
    results['duration'] = edur
    results['model'] = model
    results['gp'] = gp
    results['powell'] = powell_guess
    results['init_theta'] = theta_init
    #pull out the git hash for bsfh here.
    gh = fitterutils.run_command('cd ~/Codes/SEDfitting/bsfh/\n git rev-parse HEAD')[1][0].replace('\n','')
    results['bsfh_version'] = gh

    out = open('{1}_{0}.sampler{2:02d}_mcmc'.format(int(time.time()), rp['outfile'], 1), 'wb')
    pickle.dump(results, out)
    out.close()

