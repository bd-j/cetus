Installation (on Hyades)
=====

You need to install several packages.  Also, you will need numpy,
scipy, mpi4py, emcee, and some form of pyfits.  You should make a
directory called something like site-packages in your pfs directory.  We
are going to install all the extra modules to this directory, and then add this
directory to the PYTHONPATH environment variable, so that python can
find them.


0. Setup environment.
    1. `mkdir ~/pfs/code/site-packages`
    2.  In your .bashrc (or .bash_profile ?), add the following

	     ```
		 export SPS_HOME="/home/name/pfs/code/fsps/"
		 export PYTHONPATH=$PYTHONPATH:/home/name/pfs/code/site-packages/python-fsps/
		 export PYTHONPATH=$PYTHONPATH:/home/name/pfs/code/site-packages/sedpy/
		 export PYTHONPATH=$PYTHONPATH:/home/name/pfs/code/site-packages/bsfh/
		 ```

1. Install FSPS. 

	0. `cd ~/pfs/code/`
    1. `svn checkout http://fsps.googlecode.com/svn/trunk/ fsps`
    2. `cd fsps/src/`
    3. In the Makefile, change to an ifort compiler (``F90 = ifort``) and use compiler options ``F90_FLAGS = -O3 -cpp -fPIC``
    4. Make any changes to sps_vars.f90.  In particular, change to MILES
    5. `make all`  you will get some warnings.
    6. smoke test by running `./simple.exe`

3. Install python-FSPS.

    This will use f2py, which presumably exists (installed with numpy)
    and uses an ifort compiler.  Anyway, it is important that both
    FSPS and python-FSPS use the same fortran compiler.  I have had
    success using the default compiler options, `-cpp -fPIC`.

	1. `cd ~/pfs/code/site-packages`
    2. `git clone https://github.com/bd-j/python-fsps`
    3. `cd python-fsps`
    4. `python setup.py build_fsps` which barfs lots of text, but if
       the last line contains *removing build directory* then you are
       golden.
    5. If you are using MPI, there is a change that needs to be made
	    in `fsps.__init__.py`. Namely, you must comment out the FSPS
	    revision check, which spawns a subprocess

4. Install sedpy 
    (for dust and filter projections)

	0. `cd ~/pfs/code/site-packages`
    1. `git clone https://github.com/bd-j/sedpy`
    2. `cd sedpy/`
    3. `python setup.py install` this will fail.  need to add this package (and others) to the python path

5. Install bsfh

	0. `cd ~/pfs/code/site-packages`
    1. ``git clone https://github.com/bd-j/bsfh``

6. Install cetus

	This is the main working directory from which you will run code,
    and where results will be stored.
	
    0. `cd ~/pfs/code/`
    1. `git clone  https://github.com/bd-j/cetus`

7. command line syntax

	This is what should go in the .pb scripts
	Note that the ATLAS library that scipy uses to do the matrix
	inversions will throw assertion errors if if it is not run on the hyper
	queue. I think this is because ATLAS was compiled with that many
	processors available, and freaks out if it finds fewer
	
    1. `python bsfh.py --param_file  <param file>`
    2. `mpirun -np <np> python bsfh.py --param_file <param_file>`
