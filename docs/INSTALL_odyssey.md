Installation (on Odyssey)
=====

We are going to see if using the anaconda distribution out of the box
works.

f2py -c --help-fcompiler



Intel
==




We are going to work with intel compilers.  We are going to use conda
as an environment manager. The plan is to load intel and the intel mpi
implementation, then load python (which makes the anaconda python
version avialable), create a virtual environment, and then buil numpy,
scipy, and mpi4py in that environment, linking them against the
up-to-date intel libraries and using the intel compilers

0. Setup environment.

	0. add this to your `.bashrc`:
       ```
	   source /usr/local/bin/new-modules.sh
	   module load intel
	   module load openmpi
	   #module load intel-mkl
	   module load python
	   export APPS=/n/regal/conroy_lab/<user_name>
	   export SPS_HOME=$APPS/fsps/
	   ```
	
	1. ~~`conda create -n pympi --clone="$PYTHON_HOME"~~
	2. ~~`source activate pympi` ~~
	3. `ln -s /n/regal/conroy_lab/<user_name> regal`


0. Set up an environment

    1. `conda create -n mypympi python=2.7`
	2. `source activate mypympi`
	3. `conda install pip`
	4. `conda install cython`
	5.

1. Build numpy and scipy against MKL

   1. `wget
   http://sourceforge.net/projects/numpy/files/NumPy/1.9.0/numpy-1.9.0.tar.gz`
   2. `tar -xvf numpy-1.9.0.tar.gz; cd numpy-1.9.0`
   3. `cp site.cfg.example site.cfg`
   4. edit site.cfg:
       ```
       [mkl]
	   library_dirs = /n/sw/fasrcsw/apps/Comp/intel/13.0.079-fasrc01/intel-mkl/11.0.0.079-fasrc01/lib/intel64
	   include_dirs = /n/sw/fasrcsw/apps/Comp/intel/13.0.079-fasrc01/intel-mkl/11.0.0.079-fasrc01/include
	   lapack_libs = mkl_lapack
	   mkl_libs = mkl_rt
	   ```


1. Install FSPS. 

	0. `cd $APPS`
    1. `svn checkout http://fsps.googlecode.com/svn/trunk/ fsps`
    2. `cd fsps/src/`
    3. In the Makefile, change to an ifort compiler (``F90 = ifort``)
    and use compiler options ``F90_FLAGS = -O3 -cpp -fPIC``
 	4. Make any changes to sps_vars.f90.  In particular, change to
       MILES.  You should also change the `pset%zmet=20` lines in
       simple.f90 to `pset%zmet=4`
    5. `make all`  you might get some warnings using ifort, that's ok
    6. smoke test by running `./simple.exe`

2. Install python-fsps

    This will use f2py (which requires the numpy module to be
    loaded). It is important that both FSPS and python-FSPS use the
    same fortran compiler.  One can change the default compiler to intel by
    adding the line
	    ```
	    cmd += " --fcompiler=intelem"
	    ```
	
	to python-fsps/setup.py just before the f90flags are specified (at
    line 46). I have had success using the default compiler options in
    setup.py, `-cpp -fPIC`.

	1. `cd $APPS`
    2. `git clone https://github.com/bd-j/python-fsps`
    3. `cd python-fsps`
	5. If you are using MPI, there is a change that needs to be made
	    in `python-fsps/fsps/__init__.py`. Namely, you must comment
	    out the FSPS revision check, which spawns a subprocess, which
	    isn't allowed for slave processes in MPI.  Not sure why this
	    isn't an issue on a laptop using MPI.  Also, the accepted
	    revisions list usually lags the FSPS current revision.
    4. `python setup.py build` which barfs lots of text, but if the
       last few lines contains *removing build directory* then you are
       golden.
