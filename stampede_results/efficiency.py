import sys, os, glob
import numpy as np
import matplotlib.pyplot as pl
import bsfh.read_results as bread

def process_run(mcmc_file, model_file):
    result, pr, model = bread.read_pickles(mcmc_file, model_file=model_file)
    nburn = np.sum(result['run_params']['nburn'])
    nw, niter, ndim = result['chain'].shape
    time = result['sampling_duration']
    free_params = model.theta_labels()
    return [nw, nburn, niter], time, free_params 

mcfiles = glob.glob('*dmock*_mcmc')

speed, ncpu, hasgp = [], [], []
for i,f in enumerate(mcfiles):
    dims, dur, params = process_run(f, f.replace('_mcmc','_model'))
    print(f+'\n')
    s = dims[0] * (dims[1] + dims[2]) / dur
    speed += [s]
    nc = dims[0]/2 + 1
    ncpu += [nc]
    print(dims[0], dims[2], dur, s, nc, 'gp_jitter' in params)
    hasgp += ['gp_jitter' in params]
    
    
color = ['b','r']

fig, axes = pl.subplots()
clr =np.array(color)[np.array(hasgp).astype(int)]
axes.scatter(ncpu, speed/ncpu, marker ='o', c=clr)
axes.set_xlabel('cores')
axes.set_ylabel('Likelihood calculations/sec/core')

