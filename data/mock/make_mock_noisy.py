import sys
import numpy as np
from bsfh import read_results as bread
import pickle

def make_mock(result):
    obs= result['obs']
    obs['spectrum'] = np.exp(obs['spectrum']) * obs['scale']
    obs['unc'] = obs['spectrum'] * obs['unc']
    mock_info = result['model'].mock_info
    mock = {'obs':obs,
            'calibration': mock_info['calibration'],
            'mock_params': mock_info['params'],
            'model_params': result['model'].config_list
            }
    return mock
            
def write_mock(mock, filename):
    f = open(filename, 'w')
    pickle.dump(mock, f)
    f.close()
    
sf = 'imf_mock_young_1418786675_mcmc'
mf = 'imf_mock_young_1418786675_model'


result, pr, model = bread.read_pickles(sf, model_file=mf)
for k, v in model.mock_info['params'].iteritems():
    model.params[k] = np.atleast_1d(v)
model.params['spec_norm'] = np.array([0.0])
mock_theta = model.theta

amock = make_mock(result)
amock['mock_theta'] = mock_theta
amock['mock_snr_factor'] = 5.0
write_mock(amock, '/Users/bjohnson/Projects/cetus/data/mock/mock_cluster_SNRx5_nopoly.p')
