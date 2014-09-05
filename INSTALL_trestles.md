Installation (on Trestles)
=====

You need to install several packages.  Also, you will need numpy,
scipy, mpi4py, emcee, and some form of pyfits.  You should make a
directory called something like site-packages in your project lustre
storage space directory (`/oasis/projects/nsf/csc107/<user>`).  We are
going to install all the extra packages to this directory, and then add
this directory to the PYTHONPATH environment variable, so that python
can find them.

We are going to compile FSPS and python-FSPS using gfortran since I
cant get f2py (necessary for python-FSPS) to use Intel compilers.  It
appears that Tretles system python was built with gcc, but numpy and
scipy were built with Intel.

0. Setup environment.
    1. `mkdir /oasis/projects/nsf/<allocation>/<user>/code/site-packages`
    2.  In your .bashrc (or .bash_profile ?), add the following
	     ```
		 export PROJECT_DIR=/oasis/projects/nfs/csc107/<username>
		 export SPS_HOME="$PROJECT_DIR/code/fsps/"
		 export PYTHONPATH=$PYTHONPATH:"$PROJECT_DIR/code/site-packages/python-fsps/"
		 export PYTHONPATH=$PYTHONPATH:"$PROJECT_DIR/code/site-packages/sedpy/"
		 export PYTHONPATH=$PYTHONPATH:"$PROJECT_DIR/code/site-packages/bsfh/"
		 export PYTHONPATH=$PYTHONPATH:"$PROJECT_DIR/code/site-packages/PyFITS/lib/"
		 ```
	3. In your .bashrc file also add the following
        ```
		module purge
	    module load intel mvapich2_ib
		module load python
		module load scipy
		module load mpi4py
		```
		
1. Install FSPS. 

	0. `cd $PROJECT_DIR/code/`
    1. `svn checkout http://fsps.googlecode.com/svn/trunk/ fsps`
    2. `cd fsps/src/`
	4. Make any changes to sps_vars.f90.  In particular, change to
       MILES.  You should also change the `pset%zmet=20` lines in
       simple.f90 to `pset%zmet=4`
    4. type `module load gnu`
    3. In the Makefile, change to a gnu compiler (uncomment `F90 =
       gfortran` and comment all others) and use compiler options
       `F90_FLAGS = -O -cpp -fPIC` 
    5. `make all`  you might get some warnings.
    6. smoke test by running `./simple.exe`

3. Install python-FSPS.

    This will use f2py (which requires the numpy module to be
    loaded). It is important that both FSPS and python-FSPS use the
    same fortran compiler.  The default for f2py on Trestles seems to
    be gnu95, ~~but one can change the default compiler to intel by
    adding `-c -fcompiler=intel` to the f2py call in the setup.py
    script for python-fsps~~. I have had success using the default
    compiler options in setup.py, `-cpp -fPIC`.

	1. `cd $PROJECT_DIR/code/site-packages`
    2. `git clone https://github.com/bd-j/python-fsps`
    3. `cd python-fsps`
	5. If you are using MPI, there is a change that needs to be made
	    in `python-fsps/fsps/__init__.py`. Namely, you must comment
	    out the FSPS revision check, which spawns a subprocess, which
	    isn't allowed for slave processes in MPI.  Not sure why this
	    isn't an issue on a laptop using MPI.  Also, the accepted
	    revisions list usually lags the FSPS current revision.
	4. type `module load gnu`
    4. `python setup.py build` which barfs lots of text, but if
       the last few lines contains *removing build directory*,
       *running build_scripts*,  then you are
       golden.

4. Install pyfits
    We aren't going to try and compile the c extensions for reading
    compressed files. So just don't compress your files, ok?
	
	0. `cd $PROJECT_DIR/site-packages`
    1. `git clone https://github.com/spacetelescope/PyFITS`

4. Install sedpy 
    (for dust and filter projections)

	0. `cd $PROJECT_DIR/site-packages`
    1. `git clone https://github.com/bd-j/sedpy`
    2. `cd sedpy/`

4. Install emcee
    0. `cd $PROJECT_DIR/site-packages`
    1. `git clone https://github.com/dfm/emcee`
	
5. Install bsfh

	0. `cd $PROJECT_DIR/code/site-packages`
    1. ``git clone https://github.com/bd-j/bsfh``

6. Install cetus

	This is the main working directory from which you will run code,
    and where results will be stored.
	
    0. `cd $PROJECT_DIR/code/`
    1. `git clone  https://github.com/bd-j/cetus`

7. command line syntax

	This is what should go in the .pb scripts
	Note that the ATLAS library that scipy uses to do the matrix
	inversions will throw assertion errors if if it is not run on the hyper
	queue. I think this is because ATLAS was compiled with that many
	processors available, and freaks out if it finds fewer
	
    1. `python bsfh.py --param_file  <param file>`
    2. `mpirun -np <np> python bsfh.py --param_file <param_file>`
