from copy import deepcopy
import numpy as np
from sedpy import attenuation
from bsfh import priors, sedmodel, elines
from bsfh.datautils import load_obs_mmt
tophat = priors.tophat
import pickle


def add_wiggles(datadir="/work/03291/bdj314/code/cetus/data/", **extras):
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
    
def add_poly(obs, c, norm_band_name = 'f475w', **extras):
    norm_band = [i for i,f in enumerate(obs['filters']) if norm_band_name in f.name][0]
    c = np.array(c)
    x = obs['wavelength']/obs['filters'][norm_band].wave_effective - 1.0
    poly = np.zeros_like(x)
    powers = np.arange( 3 ) 
    poly = (x[None,:] ** powers[:,None] * c[:,None]).sum(axis = 0)
    return poly


#############
# RUN_PARAMS
#############
 
run_params = {'verbose':True,
              'outfile':'results/imf_dmock_scaling',
              'do_powell': False,
              'ftol':0.5e-4, 'maxfev':10000,
              'nwalkers':64, #'walker_factor':4
              'nburn':[32, 32, 32], 'niter':128,
              'initial_disp':0.1,
              #'nthreads':1, 'nsamplers':1,
              'mock':False,
              'debug':False,
              'data_loading_function_name': None,
              'logify_spectrum':True,
              'normalize_spectrum':True,
              'norm_band_name':'f475w',
              'rescale':True,
              'filename':'/work/03291/bdj314/code/cetus/data/mock/mock_cluster_SNRx5_nopoly_noiseless.p',
              #'filename': '/Users/bjohnson/Projects/cetus/data/mock/mock_cluster_SNRx5_nopoly_noiseless.p',
              'mock_snr_factor': 2.0,
              'noiseless': True,
              'add_mock_poly': [0.0, 0.2, -1],
              'add_wiggles': True,
              'wlo':3750., 'whi':7200.
              }

############
# OBS
#############
amock = pickle.load( open(run_params['filename']))
obs = amock['obs']
obs['unc'] *= (amock['mock_snr_factor']/ run_params['mock_snr_factor'])
mockpolypar = run_params.get('add_mock_poly', None)
wiggles = run_params.get('add_wiggles', False)
if (mockpolypar is not None) and (wiggles is False):
    poly = np.exp(add_poly(obs, mockpolypar, **run_params))
    obs['spectrum'] *= poly
    obs['unc'] *= poly
elif wiggles:
    cal_wiggles = add_wiggles()
    obs['spectrum'] *= cal_wiggles
    obs['unc'] *= cal_wiggles
    
#############
# MODEL_PARAMS
#############
model_type = sedmodel.SedModel
model_params = []

param_template = {'name':'', 'N':1, 'isfree': False,
                  'init':0.0, 'units':'', 'label':'',
                  'prior_function_name': None, 'prior_args': None}

###### Distance ##########
model_params.append({'name': 'lumdist', 'N': 1,
                     'isfree': False,
                     'init': 0.783,
                     'units': 'Mpc',
                     'prior_function': None,
                     'prior_args': None})

###### SFH ################

model_params.append({'name': 'mass', 'N': 1,
                     'isfree': True,
                     'init': 1.5e4,
                     'units': r'M$_\odot$',
                     'prior_function': tophat,
                     'prior_args': {'mini':1e2, 'maxi': 1e6}})

model_params.append({'name': 'tage', 'N': 1,
                        'isfree': True,
                        'init': 0.06,
                        'units': 'Gyr',
                        'prior_function':tophat,
                        'prior_args':{'mini':0.001, 'maxi':2.5}})

model_params.append({'name': 'zmet', 'N': 1,
                        'isfree': True,
                        'init': -0.2,
                        'units': r'$\log (Z/Z_\odot)$',
                        'prior_function': tophat,
                        'prior_args': {'mini':-1, 'maxi':0.19}})

model_params.append({'name': 'sfh', 'N':1,
                        'isfree': False,
                        'init': 0,
                        'units': None})

###### DUST ##################

model_params.append({'name': 'dust_curve', 'N': 1,
                        'isfree': False,
                        'init': attenuation.cardelli,
                        'units': None})

model_params.append({'name': 'dust2', 'N': 1,
                        'isfree': True,
                        'init': 0.5,
                        'units': r'$\tau_V$',
                        'prior_function': tophat,
                        'prior_args': {'mini':0.0, 'maxi':2.5}})

model_params.append({'name': 'dust1', 'N': 1,
                        'isfree': False,
                        'init': 0.0,
                        'units': r'$\tau_V$',
                        'prior_function': None,
                        'prior_args': None})

model_params.append({'name': 'dust_tesc', 'N': 1,
                        'isfree': False,
                        'init': 0.01,
                        'units': 'Gyr',
                        'prior_function': None,
                        'prior_args': None})

model_params.append({'name': 'dust_type', 'N': 1,
                        'isfree': False,
                        'init': 1,
                        'units': 'NOT USED'})

###### IMF ###################

model_params.append({'name': 'imf_type', 'N': 1,
                        'isfree': False,
                        'init': 2, #2 = kroupa
                        'units': None})

model_params.append({'name': 'imf3', 'N':1,
                        'isfree': True,
                        'init': 2.5,
                        'units': None,
                        'prior_function':tophat,
                        'prior_args':{'mini':1.3, 'maxi':3.3}})

###### WAVELENGTH SCALE ######

model_params.append({'name': 'zred', 'N':1,
                        'isfree': True,
                        'init': 0.00001,
                        'units': None,
                        'prior_function': tophat,
                        'prior_args': {'mini':-0.001, 'maxi':0.001}})

model_params.append({'name': 'sigma_smooth', 'N': 1,
                        'isfree': True,
                        'init': 2.2,
                        'units': r'$\AA$',
                        'prior_function': priors.lognormal,
                        'prior_args': {'log_mean':np.log(2.2)+0.25/2, 'sigma':0.25}})

model_params.append({'name': 'smooth_velocity', 'N': 1,
                        'isfree': False,
                        'init': True,
                        'units': None})

model_params.append({'name': 'min_wave_smooth', 'N': 1,
                        'isfree': False,
                        'init': 3700.0,
                        'units': r'$\AA$'})

model_params.append({'name': 'max_wave_smooth', 'N': 1,
                        'isfree': False,
                        'init': 7300.0,
                        'units': r'$\AA$'})

###### CALIBRATION ###########

polyorder = 2
polymin = [-1e1, -1e1]
polymax = [1e1, 1e1]
polyinit = [1e-2, 1e-2]

model_params.append({'name': 'poly_coeffs', 'N': polyorder,
                        'isfree': True,
                        'init': polyinit,
                        'units': None,
                        'prior_function': tophat,
                        'prior_args': {'mini':polymin, 'maxi':polymax}})
    
model_params.append({'name': 'spec_norm', 'N':1,
                        'isfree': True,
                        'init':1.00001,
                        'units': None,
                        'prior_function': tophat,
                        'prior_args': {'mini':0.2, 'maxi':5}})

model_params.append({'name': 'gp_jitter', 'N':1,
                        'isfree': True,
                        'init': 0.0001,
                        'units': 'spec units',
                        'prior_function': tophat,
                        'prior_args': {'mini':0.0, 'maxi':0.2}})

model_params.append({'name': 'gp_amplitude', 'N':1,
                        'isfree': True,
                        'init': 0.0001,
                        'units': 'spec units',
                        'prior_function': tophat,
                        'prior_args': {'mini':0.0, 'maxi':0.5}})

model_params.append({'name': 'gp_length', 'N':1,
                        'isfree': True,
                        'init': 60.0,
                        'units': r'$\AA$',
                        'prior_function': priors.lognormal,
                        'prior_args': {'log_mean':4.0 - 1.0/2.0, 'sigma':1.0}})

model_params.append({'name': 'phot_jitter', 'N':1,
                        'isfree': False,
                        'init': 0.0,
                        'units': 'mags',
                        'prior_function': tophat,
                        'prior_args': {'mini':0.0, 'maxi':0.1}})

###### EMISSION ##############

linelist = ['CaII_K', 'NaI_5891', 'NaI_5897',
            'Ha', 'NII_6585','SII_6718','SII_6732',
            'HeI_3821','HeI_4010','HeI_4027','HeI_4145','HeI_4389',
            'HeI_4473','HeI_4923','HeI_5017'
            ]
linemin = 3 * [-1] + 4 * [-1e-8]  + 8 * [-50.0 ]
linemax = 3 * [1e-8] + 4 * [10.0 ] + 8 * [50.0 ]
lineinit = 3 * [0.0 ] + 4 * [0.1e-10 ] + 8 * [0.1e-10 ]

linelist = linelist[0:3]
linemin = linemin[0:3]
linemax = linemax[0:3]
lineinit = lineinit[0:3]

nlines = len(linelist)
ewave = [elines.wavelength[l] for l in linelist]

model_params.append({'name': 'emission_rest_wavelengths', 'N': nlines,
                        'isfree': False,
                        'init': ewave,
                        'line_names': linelist,
                        'units': r'$\AA$'})

model_params.append({'name': 'emission_luminosity', 'N': nlines,
                        'isfree': False,
                        'init': lineinit,
                        'units': r'$L_\odot$',
                        'prior_function':tophat,
                        'line_names': linelist,
                        'prior_args':{'mini': linemin, 'maxi': linemax}})

model_params.append({'name': 'emission_disp', 'N': 1, 'isfree': False,
                        'init': 2.2,
                        'units': r'$\AA$',
                        'prior_function':tophat,
                        'prior_args':{'mini':1.0, 'maxi':6.0}})

