import glob
import modeldef

default_plist, default_rp = modeldef.default_parlist, modeldef.rp
plist_names = [p['name'] for p in plist]

fileroot = []
objname = {}
age = []
cstat = {'nocal':'v', 'cal':'s'}
stat ='nocal'

for f, o, a in zip(filename, objname, age):
    plist = default_plist
    rp = default_rp
    out = 

    rp['verbose'] = False
    rp['filename'] = 'data/mmt/{0}/{1}'.format(f)
    rp['objname'] = o
    rp['outfile'] = 'results/{0}_'.format(out)

    tind = plist_names.index('tage') 
    plist[tind]['init'] = a
    plist[tind]['prior_args']['mini'] = a / 100
    plist[tind]['prior_args']['maxi'] = a * 100

    modeldef.write_plist(plist, rp, out)
