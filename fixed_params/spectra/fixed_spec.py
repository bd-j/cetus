import time, sys, os
import numpy as np
import pickle

from bsfh.gp import GaussianProcess
from bsfh import model_setup

try:
    import astropy.io.fits as pyfits
except(ImportError):
    import pyfits

from bsfh import sps_basis
sps = sps_basis.StellarPopBasis(compute_vega_mags=False)
gp = GaussianProcess(None, None)

    
def get_fixed_spec(param_file, **kwargs):
    
    argdict={'param_file':None, 'sps':'sps_basis',
            'custom_filter_keys':None,
            'compute_vega_mags':False,
            'zcontinuous':True}
    argdict = model_setup.parse_args(sys.argv, argdict=argdict)
    inpar = argdict
    inpar['param_file']  = param_file


    model = model_setup.setup_model(inpar['param_file'], sps=sps)
    model.run_params['ndim'] = model.ndim
    rp = model.run_params #shortname
    model.params['cal_type'] = rp.get('cal_type', 'exp_poly')

    nw = len(sps.ssp.wavelengths)
    if nw > 6e3:
        if nw < 8e3:
            # The downsampled CKC grid
            grid = 'ckc_hs'
            sigint = 2.3
        else:
            grid = 'ckc'
            sigint = 0.0
        # We have the CKC grid but need to add in the MILES intrinsic
        # resolution (and subtract the CKC intrinsic resolution) to
        # get comparable results
        ind = [c['name'] for c in model.config_list].index('sigma_smooth')
        print(model.config_list[ind]['init'])
        model.config_list[ind]['init'] =np.sqrt((model.config_list[ind]['init'])**2 +
                                                2.54/2.35**2 - sigint**2)
        print(model.config_list[ind]['init'])
    elif nw > 2e3:
        #we have the MILES grid
        grid = 'miles'
    else:
        grid = 'basel'
        
    if model.params['cal_type'] is 'poly':
        model.rescale_parameter('spec_norm', lambda x: np.exp(x))
        model.configure()

    for k, v in kwargs.iteritems():
        model.params[k] = v
    mu, phot, x = model.mean_model(model.initial_theta, sps=sps)
    return grid, model.obs, mu, phot

if __name__ == '__main__':
    
    pfiles = ['imf_ap244_fixedparams.py', 'imf_ap552_fixedparams.py',
              'imf_dao69_fixedparams.py', 'imf_b216g267_fixedparams.py']
        
    
    dat = [list(get_fixed_spec('fixed_params/'+p)[1:]) + [p] for p in pfiles]
    grid = get_fixed_spec(pfiles[0])[0]

    f = open('fixed_spectra_{0}.p'.format(grid), 'w')
    pickle.dump(dat, f)
    f.close()
    
