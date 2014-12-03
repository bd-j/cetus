Installation (on Stampede)
===

You need to install several packages.  Also, you will need numpy, scipy, mpi4py, and f2py.  You should make a directory called something like `code` in your project lustre storage space directory.  We are going to install all the extra packages to this directory, and then add this directory to the PYTHONPATH environment variable, so that python can find them.

~~We are going to compile FSPS and python-FSPS using gfortran since I
cant get f2py (necessary for python-FSPS) to use Intel compilers.  It
appears that Tretles system python was built with gcc, but numpy and
scipy were built with Intel.~~

We are going to install FSPS and f2py using the intel compilers, so that we are not mixing compilers very much (numpy and scipy were buit with intel and seem to require the intel compilers to be loaded, even though the python was built with gcc)

Setup environment
---
* `mkdir /oasis/projects/nsf/<allocation>/<user>/code`

* In your .bashrc (or .bash_profile ?), add the following
  ```sh
  export PROJECT_DIR=/oasis/projects/nfs/<allocation>/<username>
  export $CODE=$PROJECT_DIR/code/
  export SPS_HOME=$CODE/fsps/
  export PYTHONPATH=$PYTHONPATH:$CODE/PyFITS/lib
  export PYTHONPATH=$PYTHONPATH:$CODE/emcee
  export PYTHONPATH=$PYTHONPATH:$CODE/python-fsps
  export PYTHONPATH=$PYTHONPATH:$CODE/sedpy
  export PYTHONPATH=$PYTHONPATH:$CODE/bsfh
  ```

* In your .bashrc file also add the following
  ```sh
  module purge
  module load intel/14.0.1.106 
  module load mvapich2/2.0b
  module load python
  ```

Install FSPS
---

Make sure you have all the above modules loaded, especially the intel-13 module.  We are going to use intel compilers for FSPS.

* Get the code

    ```sh
    $ cd $CODE
    $ svn checkout http://fsps.googlecode.com/svn/trunk/ fsps
    $ cd fsps/src/
    ```

* Configure and make

     * In the Makefile, change to an ifort compiler (`F90 = ifort`) and use compiler options `F90_FLAGS = -O3 -cpp -fPIC`.
     * Make any changes to `sps_vars.f90`, for example changing isochrones or spectral library or filter files and nbands.  You should also change the `pset%zmet=20` lines in `simple.f90` to `pset%zmet=4` if you are using MILES spectral library.
     * `make all`  you might get some warnings using ifort, that's ok

*  smoke test by running `./simple.exe`

Install python-fsps
---

This will use f2py (which requires the numpy module to be loaded). It is important that both FSPS and python-FSPS use the same fortran compiler.  `f2py -c --help-fcompiler` can be used to find the available compilers.  Maybe.

* Get the code

   The snippet below will put you on a special branch of my fork of python-fsps that has a number of improvements that haven't made it in to the official python-fsps yet.
   ```sh
    $ cd $CODE
    $ git clone https://github.com/bd-j/python-fsps
    $ cd python-fsps
    $ git branch custom_filters
    ```

* Change f2py compiler:

  One can change the default compiler to intel by adding the line
   ```python
   cmd += " --fcompiler=intelem"
   ```
	to `python-fsps/setup.py` just before the f90flags are specified (at line 46). I have had success using the default compiler options in setup.py, `-cpp -fPIC`.  Make sure you have the intel/13 module loaded.
	
* If you are using MPI, there is a change that needs to be made in `python-fsps/fsps/__init__.py`. Namely, you must comment out the FSPS revision check (lines 33--50), which spawns a subprocess, which isn't allowed for slave processes in MPI.  Not sure why this isn't an issue on a laptop using MPI.  Also, the accepted revisions list usually lags the FSPS current revision, so this just omits the check.

* `python setup.py build` which barfs lots of text, but if the last few lines contains *removing build directory* then you are golden.  It can be a good idea to scroll up and make sure the compiler tht was found and used is the right one (or better yet, pipe the output of this command to a logfile that can be searched later)


Install other python
---
We aren't going to try and compile the pyfits c extensions for reading compressed files. So just don't compress your files, ok?

	```sh
	cd $CODE
    git clone https://github.com/spacetelescope/PyFITS
	git clone https://github.com/dfm/emcee
	git clone https://github.com/bd-j/sedpy
	git clone https://github.com/bd-j/bsfh
	git clone  https://<gh username>:<gh password>@github.com/bd-j/cetus
	```

Command line syntax
---
`$CODE/cetus` is the main working directory from which you will run code, and where results will be stored. The following is what should go in the .pb scripts.

* single thread: `python prospectr.py --param_file  <param file>`
* multiprocessing: `ibrun  mpi_python prospectr.py --param_file <param_file>`
