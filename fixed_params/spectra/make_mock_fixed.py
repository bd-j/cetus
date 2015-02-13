import numpy as np
import pickle, os
from copy import deepcopy
from bsfh.gp import GaussianProcess
from bsfh import model_setup, sps_basis, readspec
sps = sps_basis.StellarPopBasis(compute_vega_mags=False)
gp = GaussianProcess(None, None)

if len(sps.wavelengths) > 6.5e3:
    library = 'ckc'
else:
    library = 'miles'


run_params_mmt = {'param_file': '../imf_dao69_fixedparams.py',
              'objname': 'DAO69',
              'instrument':'mmt',
              'filename':'/work/03291/bdj314/code/cetus/data/mmt/nocal/223.DAO69.s.fits',
              'phottable':'/work/03291/bdj314/code/cetus/data/apdata-cluster_6phot_v4.fits',
              'crosstable': '/work/03291/bdj314/code/cetus/data/f2_apmatch_known.fits'    
    }

run_params_lris = {'param_file': '../imf_dao69_fixedparams.py',
              'objname': 'DAO69',
              'instrument':'lris',
              'filename':'/work/03291/bdj314/code/cetus/data/lris/LRIS_B15.15.2013CL-467.blue.1d.fits',
              'phottable':'/work/03291/bdj314/code/cetus/data/apdata-cluster_6phot_v4.fits',
              'crosstable': '/work/03291/bdj314/code/cetus/data/f2_apmatch_known.fits'    
    }

run_params = run_params_lris
    
if 'bjohnson' in os.getenv('HOME'):
    for k, v in run_params_mmt.iteritems():
        if type(v) is str:
            run_params_mmt[k] = v.replace('work/03291/bdj314/code','Users/bjohnson/Projects')
    for k, v in run_params_lris.iteritems():
        if type(v) is str:
            run_params_lris[k] = v.replace('work/03291/bdj314/code','Users/bjohnson/Projects')


def get_fixed(param_file, **kwargs):

    model = model_setup.setup_model(param_file, sps=sps)

    ind = [c['name'] for c in model.config_list].index('sigma_smooth')
    model.config_list[ind]['init'] = 2.12
    for k, v in kwargs.iteritems():
        model.params[k] = v

    #mu, phot, x = model.mean_model(model.theta, sps=sps)
    return model #, mu, phot

def write_mock(mock, filename):
    f = open(filename, 'w')
    pickle.dump(mock, f)
    f.close()

if __name__ == "__main__":
    
    model = get_fixed(run_params['param_file'], gp_jitter=0.0, gp_amplitude=0.0,
                    poly_coeffs=np.array([0.0,0.0]))
    #real_obs = readspec.load_obs_mmt(**run_params_mmt)
    print(run_params_lris['crosstable'])
    real_obs = readspec.load_obs_lris(**run_params_lris)
    
    #make sure wavelength array is correct and remove the mask temporarily
    model.obs['wavelength'] = deepcopy(real_obs['wavelength'])
    model.obs['mask'] = np.ones(len(real_obs['wavelength']), dtype= bool)
    mu, phot, x = model.mean_model(model.theta, sps=sps)
    
    obs = deepcopy(real_obs)
    obs['spectrum'] = mu
    obs['maggies'] = phot
    obs['unc'] = obs['spectrum'] * (real_obs['unc']/real_obs['spectrum'])
    obs['maggies_unc'] = obs['maggies'] * (real_obs['maggies_unc']/real_obs['maggies'])
    obs['filters'] = real_obs['filters']
    #obs['phot_mask'] = np.array([True, True, True, True, False, False])
    #obs['mask'] *= ~((obs['wavelength'] > 6550) &  (obs['wavelength'] < 6590))

    amock = {}
    amock['added_noise'] = False
    amock['obs'] = obs
    amock['library'] = library
    amock['mock_params'] = deepcopy(model.params)
    outname = "{0}_{1}_noiseless.p".format(run_params['param_file'].replace('_fixedparams.py','_mock').replace('../imf_',''), run_params['instrument'])
    outname = "/Users/bjohnson/Projects/cetus/data/mock/"+outname
               
    write_mock(amock, outname)
