import os, glob, copy
import modeldef

stat ='nocal'
datadir = 'data/mmt/nocal/'

default_plist, default_rp = modeldef.default_parlist, modeldef.rp
plist_names = [p['name'] for p in default_plist]

cstat = {'nocal':'v', 'cal':'s'}
objage = {'DAO69': 0.040,
          'B192-G242': 0.250,
          'B281-G288': 1.0,
          'B216-G267': 0.200,
          'B210-M11': 0.100,
          'B380-G313':0.400,
          'M020': 0.020
          }

files = glob.glob(datadir + '*{0}.fits'.format(cstat[stat]))
for f in files:
    exp, obj, cal = os.path.basename(f).split('.')[:3]
    name = '{0}.{2}.{1}'.format(obj.lower(), stat, exp)
    age = objage[obj]
    out = name
    plist = copy.deepcopy(default_plist)
    rp = default_rp
    #print(plist[1]['prior_function'])


    rp['verbose'] = False
    rp['filename'] = f
    rp['objname'] = obj
    rp['outfile'] = 'results/' + name
    rp['maxfev'] = 10000
    rp['nburn'] = 3 * [50]
    rp['niter'] = 500
    rp['walker_factor'] = 8

    tind = plist_names.index('tage') 
    plist[tind]['init'] = age
    plist[tind]['prior_args']['mini'] = age / 10
    plist[tind]['prior_args']['maxi'] = age * 10

    modeldef.write_plist(plist, rp, 'parfiles/'+ name)
