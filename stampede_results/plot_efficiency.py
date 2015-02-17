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

mcfiles = glob.glob('*scaling*_mcmc')
mcfiles += glob.glob('*dmock*w*poly_14*_mcmc')
mcfiles += glob.glob('*dmock*wgp_14*_mcmc')

speed, ncpu, nl, hasgp = [],[], [], []
for i,f in enumerate(mcfiles):
    dims, dur, params = process_run(f, f.replace('_mcmc','_model'))
    print(f)
    nlike = dims[0] * (dims[1] + dims[2])
    nl += [nlike]
    s =  nlike / dur
    speed += [s]
    try:
        nc = int(f.split('_')[2].replace('nc',''))
    except:
        nc = dims[0]/2 + 1
    ncpu += [nc]
    print(dims[0], dims[2], dur, s, nc, 'gp_jitter' in params)
    hasgp += ['gp_jitter' in params]

ncpu = np.array(ncpu)
hasgp = np.array(hasgp)
speed = np.array(speed)
nl = np.array(nl)
    
color = np.array(['b','r'])

fig, axes = pl.subplots()
clr =color[hasgp.astype(int)]
sax = axes.scatter(ncpu[~hasgp], (speed)[~hasgp], marker ='o', c=nl[~hasgp], s = 10 * np.log(nl[~hasgp]), vmin=nl.min(), vmax=nl.max(), alpha = 0.5)
axes.scatter(ncpu[hasgp], (speed)[hasgp], marker ='*', c=nl[hasgp], s = 10 * np.log(nl[hasgp]), vmin=nl.min(), vmax=nl.max(), alpha = 0.75)
cbar = fig.colorbar(sax, ticks=[5e5, 1e6, 1.5e6], format = '%.1e')
cbar.ax.set_ylabel(r'$N_{{likelihood}}$')
axes.set_xlabel(r'$N_{{core}}$')
axes.set_ylabel(r'$N_{{likelihood}}/T_{{wall}} \, (s^{{-1}})$')

pl.show()
