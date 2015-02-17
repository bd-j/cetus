import pickle
import numpy as np
from copy import deepcopy

from bsfh.datautils import load_obs_mmt, norm_spectrum
from bsfh import sps_basis
import bsfh.read_results as bread


def write_mock(mock, filename):
    f = open(filename, 'w')
    pickle.dump(mock, f)
    f.close()

sps = sps_basis.StellarPopBasis(compute_vega_mags=False)

run_params = {'norm_band_name':'f475w',
              'verbose':True,
              'filename':'/Users/bjohnson/projects/cetus/data/mmt/nocal/020.B192-G242.s.fits',
              "phottable":"/Users/bjohnson/projects/cetus/data/f2_apcanfinal_6phot_v2.fits",
              'objname':'B192-G242',
              'wlo':3750., 'whi':7200.
              }
real_obs = load_obs_mmt(**run_params)

sf, mf = ['/Users/bjohnson/projects/cetus/stampede_results/imf_dmock_young_long_1419895042_mcmc',
          '/Users/bjohnson/projects/cetus/stampede_results/imf_dmock_young_long_1419895042_model']
result, pr, model = bread.read_pickles(sf, model_file=mf)
mockfile = result['run_params']['filename'].replace('/work/03291/bdj314/code/',
                                                    '/Users/bjohnson/projects/')
with open(mockfile) as mockf:
    amock = pickle.load( mockf)
obs = amock['obs']

# Construct spectra with no noise
amock['added_noise'] = False
mock_params= amock['mock_params']
mock_theta = amock['mock_theta']

# Generate a mock model and use the noiseless model fluxes as the observed fluxes
s, p, x = model.mean_model(mock_theta, sps=sps)
noisy_s = obs['spectrum']
noisy_p = obs['maggies']
obs['spectrum'] = s
obs['maggies'] = p
norm, pw = norm_spectrum(obs, **run_params)
obs['spectrum'] /= norm

# rescale the spectroscopic noise to the desired multiple of the real noise
old_noise = obs['unc']
obs['unc'] = obs['spectrum']/amock['mock_snr_factor']  * (real_obs['unc']/real_obs['spectrum'])[real_obs['mask']]
amock['obs'] = obs

smock = (1/(real_obs['unc']/real_obs['spectrum'])[real_obs['mask']]) * old_noise * amock['mock_snr_factor']

write_mock(amock, '/Users/bjohnson/Projects/cetus/data/mock/mock_cluster_SNRx5_nopoly_noiseless.p')
