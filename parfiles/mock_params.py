from copy import deepcopy
import numpy as np
from sedpy import attenuation
from bsfh import priors, sedmodel, elines
from bsfh.datautils import load_obs_mmt
tophat = priors.tophat

#############
# RUN_PARAMS
#############
 
run_params = {'verbose':True,
              'outfile':'results/test',
              'ftol':0.5e-5, 'maxfev':100,
              'nwalkers':64, #'walker_factor':4
              'nburn':[32, 64, 128], 'niter':128,
              'initial_disp':0.1,
              #'nthreads':1, 'nsamplers':1,
              'mock': True,
              'debug':True,
              'data_loading_function_name': "load_obs_mmt",
              'spec': True, 'phot':True,
              'logify_spectrum':False,
              'normalize_spectrum':True,
              'rescale':True,
              'filename':'/Users/bjohnson/projects/cetus/data/mmt/nocal/020.B192-G242.s.fits',
              "phottable":"/Users/bjohnson/Projects/cetus/data/f2_apcanfinal_6phot_v2.fits",
              'objname':'B192-G242',
              'wlo':3750., 'whi':7200.
              }

############
# OBS
#############
obs = load_obs_mmt(**run_params)
obs['phot_mask'] = np.array([True, True, True, True, True, True])

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
                     'init': 10e3,
                     'units': r'M$_\odot$',
                     'prior_function': tophat,
                     'prior_args': {'mini':1e2, 'maxi': 1e6}})

model_params.append({'name': 'tage', 'N': 1,
                        'isfree': True,
                        'init': 0.250,
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
                        'isfree': False,
                        'init': 2.3,
                        'units': None,
                        'prior_function':tophat,
                        'prior_args':{'mini':1.3, 'maxi':3.5}})

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
                        'prior_function': tophat,
                        'prior_args': {'mini':1.0, 'maxi':6.0}})

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
polymin = [-100, -1000]
polymax = [100, -1000]
polyinit = [0.1, 0.1]

model_params.append({'name': 'poly_coeffs', 'N': polyorder,
                        'isfree': True,
                        'init': polyinit,
                        'units': None,
                        'prior_function': tophat,
                        'prior_args': {'mini':polymin, 'maxi':polymax}})
    
model_params.append({'name': 'spec_norm', 'N':1,
                        'isfree': True,
                        'init':1,
                        'units': None,
                        'prior_function': tophat,
                        'prior_args': {'mini':0.1, 'maxi':10}})

model_params.append({'name': 'gp_jitter', 'N':1,
                        'isfree': True,
                        'init': 0.001,
                        'units': 'spec units',
                        'prior_function': tophat,
                        'prior_args': {'mini':0.0, 'maxi':0.2}})

model_params.append({'name': 'gp_amplitude', 'N':1,
                        'isfree': True,
                        'init': 0.04,
                        'units': 'spec units',
                        'prior_function': tophat,
                        'prior_args': {'mini':0.0, 'maxi':0.5}})

model_params.append({'name': 'gp_length', 'N':1,
                        'isfree': True,
                        'init': 60.0,
                        'units': r'$\AA$',
                        'prior_function': priors.lognormal,
                        'prior_args': {'log_mean':4.0, 'sigma':0.5}})

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
linemin = 3 * [-100] + 4 * [0.]  + 8 * [-50.0 ]
linemax = 3 * [0.] + 4 * [100.0 ] + 8 * [50.0 ]
lineinit = 3 * [-0.1 ] + 4 * [1.0 ] + 8 * [0.1 ]

nlines = len(linelist)
ewave = [elines.wavelength[l] for l in linelist]

model_params.append({'name': 'emission_rest_wavelengths', 'N': nlines,
                        'isfree': False,
                        'init': ewave,
                        'line_names': linelist,
                        'units': r'$\AA$'})

model_params.append({'name': 'emission_luminosity', 'N': nlines,
                        'isfree': True,
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

############
# MOCK
############

mock_info = {}
mock_info['filters'] = obs['filters']
mock_info['wavelength'] = obs['wavelength'][obs['mask']]
mock_info['params'] = {'sfh':0, 'mass':1e4, 'zmet':-0.1, 'tage':0.1,
                       'dust2':0.3, 'sigma_smooth':2.2, 'zred':1e-4,
                       'spec_norm':1.0, 'poly_coeffs':[0.0, 0.0],
                       'gp_amplitude':0.0, 'gp_jitter':0.0, 'gp_length':10.0,
                       'emission_luminosity': nlines * [0.0]}
psnr = obs['maggies']/obs['maggies_unc']
psnr[~np.isfinite(psnr)] = 3
mock_info['phot_snr'] = psnr
mock_info['spec_snr'] = (obs['spectrum']/obs['unc'])[obs['mask']]

rp_uncal = deepcopy(run_params)
rp_uncal['filename'] = rp_uncal['filename'].replace('.s.fits','.v.fits')
obs_uncal = load_obs_mmt(**rp_uncal)

mock_info['calibration'] = (obs_uncal['spectrum']/obs['spectrum'])[obs['mask']]
run_params['mock_info'] = mock_info
