Installation (on Hyades)
=====

You need to install several packages.  Also, you will need numpy,
scipy, mpi4py, emcee, and some form of pyfits.  You should make a
directory called something like site-packages in your pfs directory.  We
are going to install all the extra modules to this directory, and then add this
directory to the PYTHONPATH environment variable, so that python can
find all of these distributions.


1. In ~/pfs mkdir site-packages
2. Install FSPS.
    a. ``svn checkout http://fsps.googlecode.com/svn/trunk/ fsps``
    b. ``export SPS_HOME="/Path/to/fsps/directory/"``
    c. ``cd fsps/src/``
    d. In the Makefile, change to an ifort compiler (``F90 = ifort``) and use compiler options ``F90_FLAGS = -O3 -cpp -fPIC``
    e. Make any changes to sps_vars.f90.  In particular, change to MILES
    f. ``make all``  you will get some warnings.
    g. smoke test by running ``./simple.exe``

3. Install python-FSPS.  Note that this will use f2py, which
   presumably exists (installed with numpy) and uses an ifort
   compiler.  Anyway, it is important that both FSPS and python-FSPS
   use the same fortran compiler.  I have had success using the
   default compiler options, ``-cpp -fPIC``
    a. ``git clone https://github.com/bd-j/python-fsps``
    b. ``cd python-fsps``
    c. ``python setup.py build_fsps`` which barfs lots of stuff, but if the last line is 'removing build directory' then you are golden.
    d.  do something to put this on the python path

4. Install sedpy (for dust and filter projections)
    a. ``git clone https://github.com/bd-j/sedpy``
    b. ``cd sedpy/``
    c. ``python setup.py install`` this will fail.  need to add this package (and others) to the python path

5. bsfh
    a. ``git clone https://github.com/bd-j/bsfh``

6. command line syntax
    a. python bsfh.py --param_file = <param file>
    b. mpirun -np 4 python bsfh.py --param_file <param_file>
