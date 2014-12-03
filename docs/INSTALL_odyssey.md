Installation (on Odyssey)
===

We are going to use the conroy_lab stack. We are going to work with intel compilers.


Setup Environment
---

Add this to your `.bashrc`:

```sh
export APPS=/n/regal/conroy_lab/<user_name>/code
export SPS_HOME=$APPS/fsps/
module load hpc/intel-compilers-13.0.079
module load hpc/intel-mkl-11.0.0.079 
module load centos6/python-2.7.8 
module load centos6/cython-0.21.1_python-2.7.8
module load centos6/numpy-1.9.1_python-2.7.8
module load centos6/scipy-0.14.0_python-2.7.8
```

### Python Codes ###

We don't have root access so things like pip won't work. If we were good we would use some sort of environment manager like virtualenv, but instead we are just going to add all our python code explicitly to the python path.  So put the following in your `.bashrc`

```sh
export PYTHONPATH=$PYTHONPATH:$APPS/emcee
export PYTHONPATH=$PYTHONPATH:$APPS/python-fsps
export PYTHONPATH=$PYTHONPATH:$APPS/sedpy
export PYTHONPATH=$PYTHONPATH:$APPS/bsfh
```

### MPI ###

There are two different MPI implementations available to us.  openMPI is probably safest, we will eventually want tot do tests to see if mvapich2 is any faster.  But try openMPI first 

* openMPI

  If using openMPI, add the following to your `.bashrc`:
  ```sh
  module load centos6/openmpi-1.8.3_intel-13.0.079
  module load centos6/mpi4py-1.3.1_python-2.7.8_openmpi-1.8.3_intel-13.0.079
  module load centos6/hdf5-1.8.11_openmpi-1.8.3_intel-13.0.079
  module load centos6/h5py-2.3.1_python-2.7.8_openmpi-1.8.3_intel-13.0.079
  module load centos6/astropy-0.4.2_python-2.7.8
  ```
	   
* mvapich2
	   
   If using mvapich2, add the following to your `.bashrc` instead:
   ```sh
   module load centos6/mvapich2-2.1a_intel-13.0.079
   module load centos6/mpi4py-1.3.1python-2.7.8mvapich2-2.1a_intel-13.0.079
   module load centos6/hdf5-1.8.11mvapich2-2.1aintel-13.0.079
   module load centos6/h5py-2.3.1python-2.7.8mvapich2-2.1a_intel-13.0.079
   module load centos6/astropy-0.4.2_python-2.7.8
   ```

### Interactive Job ###
For the compilation of codes below, it appears that some performance gains can be made by compiling on one of the compute nodes rather than on a login node.  So, lets set up an interative job running a shell on one of the compute nodes for doing the compilations.  The job and shell will inherit all the environment variables set previously.  We will ask for lots of memory since FSPS is RAM intensive.

* First `source ~/.bashrc`

* `srun -p interact --pty --mem 2000 -t 0-6:00 /bin/bash`

You can quit out of the interactive job with `exit`

Install FSPS
---

Make sure you have all the above modules loaded, especially the intel-13 module.  We are going to use intel compilers for FSPS.  You can type `which ifort` to see which compiler is loaded, it should return something like `/n/sw/intel_cluster_studio-2013/bin/ifort`.

* Get the code

    ```sh
    $ cd $APPS
    $ svn checkout http://fsps.googlecode.com/svn/trunk/ fsps
    $ cd fsps/src/
    ```

* Configure and make

     * In the Makefile, change to an ifort compiler (`F90 = ifort`) and use compiler options `F90_FLAGS = -O3 -funroll-loops -cpp -fPIC`.
     * Make any changes to `sps_vars.f90`, for example changing isochrones or spectral library or filter files and nbands.  You should also change the `pset%zmet=20` lines in `simple.f90` to `pset%zmet=4` if you are using MILES spectral library.
     * `make all`  you might get some warnings using ifort, that's ok

*  smoke test by running `./simple.exe`

Install python-fsps
---

This will use f2py (which requires the numpy module to be loaded). It is important that both FSPS and python-FSPS use the same fortran compiler.  `f2py -c --help-fcompiler` can be used to find the available compilers.  You should see near the bottom of the output from this command, under `Fortran compilers found:` the line `--fcompiler=intelem  Intel Fortran Compiler for 64-bit apps (13.0)`.

* Get the code

   The snippet below will put you on a special branch of my fork of python-fsps that has a number of improvements that haven't made it in to the official python-fsps yet.
   ```sh
   $ cd $APPS
   $ git clone https://github.com/bd-j/python-fsps
   $ cd python-fsps
   $ git checkout -b custom_filters origin/custom_filters
   ```

* Change f2py compiler:

  One can change the default compilers to intel by adding the lines
  ```python
  cmd += " --compiler=intelem"
  cmd += " --fcompiler=intelem"
  ```
	to `python-fsps/setup.py` just before the f90flags are specified (at line 46). I have had success using the default compiler options in setup.py, `-cpp -fPIC`.  Again, make sure you have the intel/13 module loaded.
	
* If you are using MPI, there is a change that needs to be made in `python-fsps/fsps/__init__.py`. Namely, you must comment out the FSPS revision check (lines 33--50), which spawns a subprocess, which isn't allowed for slave processes in MPI.  Not sure why this isn't an issue on a laptop using MPI.  Also, the accepted revisions list usually lags the FSPS current revision, so this just omits the check.


* `python setup.py build` which barfs lots of text, but if the last few lines contains *removing build directory* then you are golden.  It can be a good idea to scroll up and make sure the compiler tht was found and used is the right one (or better yet, pipe the output of this command to a logfile that can be searched later)

* exit out of the interactive job

Install other Python codes
---

```sh
$ cd $APPS
$ git clone https://github.com/dfm/emcee
$ git clone https://github.com/bd-j/sedpy
$ git clone https://github.com/bd-j/bsfh
```

Test
---

Fire up python

```python
import fsps
sps = fsps.StellarPopulation(zcontinuous=True)
sps.params['logzsol'] = -0.1
w, s = sps.get_spectrum(tage=0.1, peraa=True)
```

If that runs, try the little `mpi_test.py` script with the following job submission script
