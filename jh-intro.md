% Savio Jupyterhub training: JupyterHub on the Berkeley Savio high-performance computing cluster
% March 8, 2017


# Introduction

We'll do this mostly as a demonstration. I encourage you to login to your account and try out the various examples yourself as we go through them.

The first half of this material is based on the Savio JupyterHub documention we have prepared and continue to prepare, available at [http://research-it.berkeley.edu/services/high-performance-computing/XXXX](http://research-it.berkeley.edu/services/high-performance-computing/XXXX).

The materials for this tutorial are available using git at [https://github.com/ucberkeley/savio-training-jupyterhub-2017](https://github.com/ucberkeley/savio-training-jupyterhub-2017) or simply as a [zip file](https://github.com/ucberkeley/savio-training-jupyterhub-2017/archive/master.zip).

These *parallel.html* and *parallel_slides.html* files were created from *parallel.md* by running `make all` (see *Makefile* for details on how that creates the html files).

Please see this [zip file](https://github.com/ucberkeley/savio-training-jupyterhub-2017/archive/master.zip) for materials from our introductory training on August 2, including accessing Savio, data transfer, and basic job submission.


# Outline

This training session will cover the following topics:

 - Software installation
     - Installing third-party software
     - Installing Python and R packages that rely on third-party software
         - Python example
         - R example
 - Parallelization strategies
     - Some general principles and concepts    
         - shared vs. distributed memory; communication overhead
         - hybrid and nested parallelization
         - load-balancing and prescheduling          
     - Overview of software tools
 - Setting up a parallel job in SLURM
     - Job submission overview
     - SLURM flags
     - SLURM environment variables
 - Basic parallelization in Python and R
     - iPython examples
         - basic example on multiple nodes and one node
         - hybrid parallelization example: threaded linear algebra
     - R examples
         - basic example on multiple nodes and one node
         - hybrid parallelization example: threaded linear algebra
 - High-throughput computing with ht_helper  
 - Wrap-up


# Third-party software installation - overview

In general, third-party software will provide installation instructions on a webpage, Github README, or install file inside the package source code.

The key for installing on Savio is making sure everything gets installed in your own home, project, or scratch directory and making sure you have the packages on which the software depends on also installed or loaded from the Savio modules. 

A common installation approach is the GNU build system (Autotools), which involves three steps: configure, make, and make install.

  - *configure*: this queries your system to find out what tools (e.g., compilers and other packages) you have available to use in building and using the software
  - *make*: this compiles the source code in the software package
  - *make install*: this moves the compiled code (library files and executables) and header files and the like to their permanent home 

# Third-party software installation - examples

Here's are a couple examples of installing a piece of software in your home directory

### yaml package example

```
mkdir software 
mkdir src  # set up directory for source packages
# install yaml, an optional dependency for Python yaml package
cd src
PKG=yaml
mkdir ${PKG}
cd ${PKG}
V=0.1.7
INSTALLDIR=~/software/${PKG}
wget http://pyyaml.org/download/libyaml/${PKG}-${V}.tar.gz
tar -xvzf ${PKG}-${V}.tar.gz
cd ${PKG}-${V}
# --prefix is key to install in directory you have access to
./configure  --prefix=$INSTALLDIR | tee ../configure.log
make | tee ../make.log
make install | tee ../install.log
```

### geos package example

```
cd ~/src
# install geos, needed for rgeos R package
V=3.5.0
PKG=geos
mkdir ${PKG}
cd ${PKG}
INSTALLDIR=~/software/${PKG}
wget http://download.osgeo.org/${PKG}/${PKG}-${V}.tar.bz2
tar -xvjf ${PKG}-${V}.tar.bz2
cd ${PKG}-${V}
./configure --prefix=$INSTALLDIR | tee ../configure.log   
make | tee ../make.log
make install | tee ../install.log
```


For Cmake, the following may work (this is not a worked example, just some template code):
```
PKG=foo
INSTALLDIR=~/software/${PKG}
cmake -DCMAKE_INSTALL_PREFIX=${INSTALLDIR} . | tee ../cmake.log
```

# Third-party software installation - final steps

To use the software you just installed as a dependency of other software you want to install (e.g., Python or R packages), you often need to make Linux aware of the location of the following in your newly-installed software:

  - library files (for other software to link against)
  - executables (for other software to call), and 
  - header files (for other software to compile against).

For library files, you may need this:

```
# needed in the geos example to install the rgeos R package
export LD_LIBRARY_PATH=${INSTALLDIR}/lib:${LD_LIBRARY_PATH}
```

This is because Linux only looks in certain directories for the location of .so library files. A clue that you may need this is seeing an error message such as `libfoo.so` not found.

For executables (binaries), you may need this: 

```
# needed in the geos example to install the rgeos R package
export PATH=${INSTALLDIR}/bin:${PATH}
echo ${PATH}
```

 Linux only looks in certain directories for executables.

For header files, you generally need to do something specific for the subsequent software you are installing. If you see comments about *.h* files not being found, you need to make sure the compiler can find the *include* directory that contains those files.

# Installing Python and R packages 


```
module load python/2.7.8
module load pip
PYPKG=pyyaml
PKGDIR=~/software/yaml
pip install --user ${PYPKG}
ls .local/lib/python2.7/site-packages
# needs to find header files
pip install --user --ignore-installed --global-option=build_ext  \
    --global-option="-I/${PKGDIR}/include" ${PYPKG}
# no -lyaml (needs to find library) files 
# in this case setting LD_LIBRARY_PATH does not work for some reason
pip install --user --ignore-installed --global-option=build_ext \
    --global-option="-I/${PKGDIR}/include" \
    --global-option="-L/${PKGDIR}/lib" ${PYPKG}
```

```
# in this case, setting LD_LIBRARY_PATH works (and we also need to have set PATH)
PKGDIR=~/software/geos
export LD_LIBRARY_PATH=${PKGDIR}/lib:${LD_LIBRARY_PATH}
export PATH=${PKGDIR}/bin:${PATH}
module load r
Rscript -e "install.packages('rgeos', repos = 'http://cran.cnr.berkeley.edu', \
lib = Sys.getenv('R_LIBS_USER'))"
```

You may sometimes need to use the `configure.args` or `configure.vars` argument to provide information on the location of `include` and `lib` directories of dependencies. The Savio help email can provide support for complicated installations.

# Installation for an entire group

You can follow the approaches on the previous slides, but have your installation directory be on `/global/home/groups/${GROUP}` or `/global/scratch/${USER}` instead.

If you change the UNIX permissions of the installed files to allow your group members access, then they should be able to use the software too.

For example, you would need to do something lik this:


```
PKGDIR=rgeos
chmod g+r -R ~/software/${PKGDIR}
chmod g+x ~/software/${PKGDIR}/bin/*
chmod g+rx ~ ~software ~software/${PKGDIR}
chmod g+rx ~/software/${PKGDIR}/{bin,include,lib}
```

This will allow reading by group members for all files in the directory and execution for the group members on the executables in `bin` (as well as access through to the subdirectories using the +rx at the higher-level directories).

You may also want to set up your own module that allows you to easily set your environment so that the software is accessible for you (and possibly others in your group). To do this you need to:

First we'll need a directory in which to store our module files:

```
MYMODULEPATH=~/software/modfiles
mkdir ${MYMODULEPATH}
export MODULEPATH=${MODULEPATH}:${MYMODULEPATH}  # good to put this in your .bashrc
mkdir ${MYMODULEPATH}/geos
```

Now we create a module file for the version (or one each for multiple versions) of the software we have installed. E.g., for our geos installation we would edit  `${MPATH}/geos/3.5.0` based on looking at examples of other module files. An example module file for our geos example is *example-modulefile*.

```
cp example-modfile ${MYMODULEPATH}/geos/3.5.0
```

Or see some of the Savio system-level modules in `/global/software/sl-6.x86_64/modfiles/langs`. 

```
cat /global/software/sl-6.x86_64/modfiles/langs/python/2.7.8
```

There is also some high-level information on modules in [http://research-it.berkeley.edu/services/high-performance-computing/accessing-and-installing-software#Chaining](http://research-it.berkeley.edu/services/high-performance-computing/accessing-and-installing-software#Chaining).

# Parallel processing terminology

  - *cores*: We'll use this term to mean the different processing
units available on a single node.
  - *nodes*: We'll use this term to mean the different computers,
each with their own distinct memory, that make up a cluster or supercomputer.
  - *processes* or *SLURM tasks*: computational instances executing on a machine; multiple
processes may be executing at once. Ideally we have no more processes than cores on
a node.
  - *threads*: multiple paths of execution within a single process;
the OS sees the threads as a single process, but one can think of
them as 'lightweight' processes. Ideally when considering the processes
and their threads, we would have no more processes and threads combined
than cores on a node.
 - *computational tasks*: We'll use this to mean the independent computational units that make up the job you submit
    - each *process* or *SLURM task* might carry out one computational task or might be assigned multiple tasks sequentially or as a group.

# Parallelization strategies

The following are some basic principles/suggestions for how to parallelize
your computation.


# Parallelization strategies (1)

Should I use one machine/node or many machines/nodes?

 - If you can do your computation on the cores of a single node using
shared memory, that will be faster than using the same number of cores
(or even somewhat more cores) across multiple nodes. Similarly, jobs
with a lot of data/high memory requirements that one might think of
as requiring Spark or Hadoop may in some cases be much faster if you can find
a single machine with a lot of memory.
 - That said, if you would run out of memory on a single node, then you'll
need to use distributed memory.
 - If you have so much data that you overwhelm the amount that can fit in RAM on one machine, Spark may be useful and [is available on Savio](http://research-it.berkeley.edu/services/high-performance-computing/tips-using-brc-savio-cluster#q-how-can-i-run-spark-jobs-)
 - If you have data that will fit in memory on one machine, Python, MATLAB, C/C++, and R may be your best bet.

# Parallelization strategies (2)

What level or dimension should I parallelize over?

 - If you have nested loops, you often only want to parallelize at
one level of the code. Keep in mind whether your linear algebra is being
threaded. Often you will want to parallelize over a loop and not use
threaded linear algebra.
 - Often it makes sense to parallelize the outer loop when you have nested
loops.
 - You generally want to parallelize in such a way that your code is
load-balanced and does not involve too much communication. 

 - If you have a small-ish number of long tasks, then a hybrid parallelization scheme may make sense.
 - E.g., if each task involves substantial linear algebra, you might have multiple cores on a node assigned to each task so that the linear algebra can be done in parallel.

# Parallelization strategies (3)

How do I balance communication overhead with keeping my cores busy?

 - If you have very few tasks, particularly if the tasks take different
amounts of time, often some of the processors will be idle and your code
poorly load-balanced.
 - If you have very many tasks and each one takes little time, the communication
overhead of starting and stopping the tasks will reduce efficiency.
 - Avoid having a very small number of jobs, each of which (or some of which) take hours to days to run
 - Avoid having a very large number of jobs, each of which takes milliseconds to run

# Parallelization strategies (4)

Should multiple tasks be pre-assigned to a process (i.e., a worker) (sometimes called *prescheduling*) or should tasks
be assigned dynamically as previous tasks finish? 

 - If you have many tasks that each take similar time: preschedule the tasks to reduce communication. 
 - If you have few tasks or tasks with highly variable completion times: improve load-balancing by NOT prescheduling
 - For R in particular, some of R's parallel functions allow you to say whether the 
tasks should be prescheduled. E.g., `library(Rmpi); help(mpi.parSapply)` gives some information.
 - Or you may want to manually aggregate your tasks if each one is very quick.

# Parallelization tools - shared memory

 - shared memory parallelization (one machine, multiple cores)
    - threaded linear algebra in R, Python, MATLAB 
        - R and Python require specific installation with parallel linear algebra support from BLAS packages such as OpenBLAS or MKL
    - parallelization of independent computations
        - iPython (example later) or other Python packages (e.g., *pp*, *multiprocessing*)
        - various R packages (*foreach* + *doParallel*, *mclapply*, *parLapply*)
        - *parfor* in MATLAB
    - openMP for writing threaded code in C/C++
    - GPUs (available on Savio): 
        - various machine learning packages with GPU back-end support
        - direct coding in CUDA or openCL

# Parallelization tools - distributed memory

 - distributed parallelization (multiple nodes)
    - parallelization of independent computations
        - iPython (example later) or other Python packages
        - various R packages (*foreach* + *doMPI*, *foreach* + *doSNOW*, *pbdR*)
        - *parfor* in MATLAB with MATLAB DCS
    - MPI for more tightly-coupled parallelization
        - MPI in C/C++
        - *mpi4py* for Python
        - *pbdR* (*pbdMPI*) and *Rmpi* for R
    - Spark/Hadoop for parallelized MapReduce computations across multiple nodes
        - data spread across multiple nodes and read into collective memory


# Submitting jobs: accounts and partitions

All computations are done by submitting jobs to the scheduling software that manages jobs on the cluster, called SLURM.

When submitting a job, the main things you need to indicate are the project account you are using (in some cases you might have access to multiple accounts such as an FCA and a condo) and the partition.

You can see what accounts you have access to and which partitions within those accounts as follows:

```
sacctmgr -p show associations user=${USER}
```

Here's an example of the output for a user who has access to an FCA, a condo, and a special partner account:
```
Cluster|Account|User|Partition|Share|GrpJobs|GrpTRES|GrpSubmit|GrpWall|GrpTRESMins|MaxJobs|MaxTRES|MaxTRESPerNode|MaxSubmit|MaxWall|MaxTRESMins|QOS|Def QOS|GrpTRESRunMins|
brc|co_stat|paciorek|savio2_gpu|1||||||||||||savio_lowprio|savio_lowprio||
brc|co_stat|paciorek|savio2_htc|1||||||||||||savio_lowprio|savio_lowprio||
brc|co_stat|paciorek|savio|1||||||||||||savio_lowprio|savio_lowprio||
brc|co_stat|paciorek|savio_bigmem|1||||||||||||savio_lowprio|savio_lowprio||
brc|co_stat|paciorek|savio2|1||||||||||||savio_lowprio,stat_normal|stat_normal||
brc|fc_paciorek|paciorek|savio2|1||||||||||||savio_debug,savio_normal|savio_normal||
brc|fc_paciorek|paciorek|savio|1||||||||||||savio_debug,savio_normal|savio_normal||
brc|fc_paciorek|paciorek|savio_bigmem|1||||||||||||savio_debug,savio_normal|savio_normal||
brc|ac_scsguest|paciorek|savio2_htc|1||||||||||||savio_debug,savio_normal|savio_normal||
brc|ac_scsguest|paciorek|savio2_gpu|1||||||||||||savio_debug,savio_normal|savio_normal||
brc|ac_scsguest|paciorek|savio2|1||||||||||||savio_debug,savio_normal|savio_normal||
brc|ac_scsguest|paciorek|savio_bigmem|1||||||||||||savio_debug,savio_normal|savio_normal||
brc|ac_scsguest|paciorek|savio|1||||||||||||savio_debug,savio_normal|savio_normal||
```

If you are part of a condo, you'll notice that you have *low-priority* access to certain partitions. For example I am part of the statistics cluster *co_stat*, which owns some Savio2 nodes and therefore I have normal access to those, but I can also burst beyond the condo and use other partitions at low-priority (see below).

In contrast, through my FCA, I have access to the savio, savio2, and big memory partitions.

# Submitting a batch job

Let's see how to submit a simple job. If your job will only use the resources on a single node, you can do the following. 


Here's an example job script (*test.sh*) that I'll run. You'll need to modify the --account value and possibly the --partition value.


        #!/bin/bash
        # Job name:
        #SBATCH --job-name=test
        #
        # Account:
        #SBATCH --account=co_stat
        #
        # Partition:
        #SBATCH --partition=savio2
        #
        # Wall clock limit (30 seconds here):
        #SBATCH --time=00:00:30
        #
        ## Command(s) to run:
        module unload python # make sure python/2 not loaded
        module load python/3.2.3 numpy
        python3 calc.py >& calc.out


Now let's submit and monitor the job:

```
sbatch test.sh

squeue -j JOB_ID

wwall -j JOB_ID
```

Note that except for the *savio2_htc*  and *savio2_gpu* partitions, all jobs are given exclusive access to the entire node or nodes assigned to the job (and your account is charged for all of the cores on the node(s). 

# Parallel job submission

If you are submitting a job that uses multiple nodes, you'll need to carefully specify the resources you need. The key flags for use in your job script are:

 - `--nodes` (or `-N`): number of nodes to use
 - `--ntasks-per-node`: number of SLURM tasks (i.e., processes) one wants to run on each node
 - `--cpus-per-task` (or `-c`): number of cpus to be used for each task

In addition, in some cases it can make sense to use the `--ntasks` (or `-n`) option to indicate the total number of SLURM tasks and let the scheduler determine how many nodes and tasks per node are needed. In general `--cpus-per-task` will be 1 except when running threaded code.  


Here's an example job script (see also *mpi-example.sh*) for a job that uses MPI for parallelizing over multiple nodes:

       #!/bin/bash
       # Job name:
       #SBATCH --job-name=test
       #
       # Account:
       #SBATCH --account=account_name
       #
       # Partition:
       #SBATCH --partition=partition_name
       #
       # Number of MPI tasks needed for use case (example):
       #SBATCH --ntasks=40
       #
       # Processors per task:
       #SBATCH --cpus-per-task=1
       #
       # Wall clock limit:
       #SBATCH --time=00:00:30
       #
       ## Command(s) to run (example):
       module load intel openmpi
       mpirun ./a.out



Some common paradigms are:

 - MPI jobs that use *one* CPU per task for each of *n* SLURM tasks
     - `--ntasks=n --cpus-per-task=1` 
     - `--nodes=x --ntasks-per-node=y --cpus-per-task=1` 
        - assumes that `n = x*y`
 - openMP/threaded jobs that use *c* CPUs for *one* SLURM task
     - `--nodes=1 --ntasks-per-node=1 --cpus-per-task=c` 
 - hybrid parallelization jobs (e.g., MPI+threading) that use *c* CPUs for each of *n* SLURM tasks
     - `--ntasks=n --cpus-per-task=c`
     - `--nodes=x --ntasks-per-node=y cpus-per-task=c` 
        - assumes that `y*c` equals the number of cores on a node and that `n = x*y` equals the total number of tasks

In general, the defaults for the various flags will be 1 so some of the flags above are not strictly needed.

There are lots more examples of job submission scripts for different kinds of parallelization (multi-node (MPI), multi-core (openMP), hybrid, etc.) [here](http://research-it.berkeley.edu/services/high-performance-computing/running-your-jobs#Job-submission-with-specific-resource-requirements). We'll discuss some of them below.

# SLURM environment variables

When you write your code, you may need to specify information in your code about the number of cores to use. SLURM will provide a variety of variables that you can use in your code so that it adapts to the resources you have requested rather than being hard-coded. 

Here are some of the variables that may be useful: SLURM_NTASKS, SLURM_CPUS_PER_TASK, SLURM_NODELIST, SLURM_NNODES.

Here's how you can access those variables in your code:

```
import os                               ## Python
int(os.environ['SLURM_NTASKS'])         ## Python

as.numeric(Sys.getenv('SLURM_NTASKS'))  ## R

str2num(getenv('SLURM_NTASKS')))        ## MATLAB
```

To use multiple cores on a node (and thereby fully utilize the node that will be exclusively assigned to your job), be careful if you only specify `--nodes`, as the environment variables will only indicate one task per node.

You can experiment with what the environment variables are set to as follows:

```
cat > env.sh <<EOF
#!/bin/bash
env >> env.out
EOF

sbatch -A co_stat -p savio --ntasks-per-node=5 --cpus-per-task=4 \
       -N 2 -t 0:05 env.sh

grep SLURM env.out 
```

# Example use of standard software: Python

Let's see a basic example of doing an analysis in Python across multiple cores on multiple nodes. We'll use the airline departure data in */global/scratch/paciorek/bayArea.csv* (which should be readable by other users).

Here we'll use *IPython* for parallel computing. The example is a bit contrived in that a lot of the time is spent moving data around rather than doing computation, but it should illustrate how to do a few things.

First we'll install a Python package not already available as a module.

```
# remember to do I/O off scratch
ls -l /global/scratch/paciorek/bayArea.csv # check file is there
# install Python package
module load pip
# trial and error to realize which package dependencies available in modules...
module load python/2.7.8 numpy scipy six pandas pytz
pip install --user statsmodels
```

Now we'll start up an interactive session, though often this sort of thing would be done via a batch job.

```
srun -A co_stat -p savio2  --nodes=2 --ntasks-per-node=24 -t 30:0 --pty bash
```

Now we'll start up a cluster using IPython's parallel tools. To do this across multiple nodes within a SLURM job, it goes like this:
 
```
module load python/2.7.8 ipython pandas scipy
ipcontroller --ip='*' &
sleep 5
# next line will start as many ipengines as we have SLURM tasks 
#   because srun is a SLURM command
srun ipengine &  
sleep 15  # wait until all engines have successfully started
ipython
```


Here's our Python code (also found in *parallel.py*) for doing an analysis across multiple strata/subsets of the dataset in parallel. Note that the *load_balanced_view* syntax is so that the computations are done in a load-balanced fashion, which is important for tasks that take different amounts of time to complete.

```
from IPython.parallel import Client
c = Client()
c.ids

dview = c[:]
dview.block = True
dview.apply(lambda : "Hello, World")

lview = c.load_balanced_view()
lview.block = True

import pandas 
dat = pandas.read_csv('/global/scratch/paciorek/bayArea.csv', header = None)
dat.columns = ('Year','Month','DayofMonth','DayOfWeek','DepTime','CRSDepTime',
'ArrTime','CRSArrTime','UniqueCarrier','FlightNum','TailNum',
'ActualElapsedTime','CRSElapsedTime','AirTime','ArrDelay','DepDelay',
'Origin','Dest','Distance','TaxiIn','TaxiOut','Cancelled','CancellationCode',
'Diverted','CarrierDelay','WeatherDelay','NASDelay','SecurityDelay',
'LateAircraftDelay')

dview.execute('import statsmodels.api as sm')

dat2 = dat.loc[:, ('DepDelay','Year','Dest','Origin')]
dests = dat2.Dest.unique()

mydict = dict(dat2 = dat2, dests = dests)
dview.push(mydict)

def f(id):
    sub = dat2.loc[dat2.Dest == dests[id],:]
    sub = sm.add_constant(sub)
    model = sm.OLS(sub.DepDelay, sub.loc[:,('const','Year')])
    results = model.fit()
    return results.params

import time
time.time()
parallel_result = lview.map(f, range(len(dests)))
#result = map(f, range(len(dests)))
time.time()

# some NaN values because all 'Year' values are the same for some destinations

parallel_result
```

And we'll stop our cluster. 

```
ipcluster stop
```

# Modifications to the example for single node or JupyterHub use

Note that none of the stanza involving the cluster startup with *ipcontroller* and *ipengine* nor the use of `ipcluster start` is necessary if using ipython parallel through Savio's JupyterHub portal.

If we were running the job on a single node, we could start everything up in a single call to *ipcluster* without the need for *ipcontroller* and *ipengine*:

```
module load python/2.7.8 ipython
ipcluster start -n $SLURM_NTASKS_PER_NODE &
ipython
```


# Example use of standard software: Python via JupyterHub

This is still in its test phase but will be a new service offering from Savio.

1. Connect to [https://ln000.brc.berkeley.edu](https://ln000.brc.berkeley.edu) (this is the test site, once we decide to push it to production and once we have the hardware in place we will replace it). Note currently we are using a self-signed SSL certificate so you will need to accept it. We will get a valid certificate once it goes into production.

2. Just after logging in with your BRC username and one-time password (OTP), the initial Jupyter screen presents a "Start My Server" button. Click that button.

3. On the next screen, "Spawner options", you will see a dropdown box to select how you want the Notebook server to be spawned. By default you should select "Local Server" for testing purpose. If you have the requirement to run serious compute with the Notebook it is recommended to select "Savio" or "Savio2" which will spawn into Savio and Savio2 partitions respectively. Currently these two options are limited to a single node and 8 hours of runtime.

4. Select "Local Server" and now you should land in the home directory. From the "New" dropdown menu (next to 'Upload' near the top right of the screen) select "Python 2" and you should be in a Notebook with full support of the python/2.7.8 module tree. Don't select "Python 3" which is just there to support Jupyter and is not a complete environment. We will fix that later.

# Example of hybrid parallelization with Python using threaded linear algebra

Here we'll run a job that uses multiple threads for linear algebra. 

```
srun -A co_stat -p savio --ntasks-per-node=1 --cpus-per-task=4 -N 1 \
      -t 5:00 --pty bash 
module load python/2.7.8 numpy
python < linear_algebra.py &
top  # should see >100% CPU in use 
```

Python on Savio is set up to use Atlas for threaded linear algebra, but unlike MKL or openBLAS, I don't know of a way to control the maximum number of threads used...

Suppose our parallel computational tasks each did linear algebra and we wanted to run multiple computational tasks, each with multiple cores for the linear algebra. 

We can set up an iPython parallel cluster as previously but making sure we have multiple cores per computational task. Note that an example *hybrid.py* does not actually exist so this is just a template, not a worked example.

```
#!/bin/bash
# Job name:
#SBATCH --job-name=test
#
# Account:
#SBATCH --account=co_stat
#
# Partition:
#SBATCH --partition=savio2
#
# Number of tasks (2 nodes' worth)
#SBATCH --ntasks=12
#
# Processors per task:
#SBATCH --cpus-per-task=4
#
# Wall clock limit:
#SBATCH --time=04:00:00
#
module load python/2.7.8 ipython gcc openmpi
ipcontroller --ip='*' &
sleep 5
srun ipengine &  # will start as many ipengines as we have SLURM tasks because srun is a SLURM command
sleep 15  # wait until all engines have successfully started
ipython
ipcluster start -n $SLURM_NTASKS &
ipython < hybrid.py >& hybrid.out  
ipcluster stop
```

# Example use of standard software: R on multiple nodes

Let's see a basic example of doing an analysis in R across multiple cores on multiple nodes. We'll use the airline departure data in *bayArea.csv*.

We'll do this interactively though often this sort of thing would be done via a batch job.


```
# remember to do I/O off scratch
module load r Rmpi
# we need the doMPI package installed
Rscript -e "install.packages('doMPI', repos = 'http://cran.cnr.berkeley.edu', lib = Sys.getenv('R_LIBS_USER'))"

srun -A co_stat -p savio2  -N 2 --ntasks-per-node=24 -t 30:0 --pty bash
module load gcc openmpi r Rmpi
mpirun R CMD BATCH --no-save parallel-multi.R parallel-multi.Rout &
```

Now here's the R code (see *parallel-multi.R*) we're running:
```
library(doMPI)

cl = startMPIcluster()  # by default will start one fewer slave than available SLURM tasks
registerDoMPI(cl)
clusterSize(cl) # just to check

dat <- read.csv('/global/scratch/paciorek/bayArea.csv', header = FALSE,
                stringsAsFactors = FALSE)
names(dat)[16:18] <- c('delay', 'origin', 'dest')
table(dat$dest)

destVals <- unique(dat$dest)

# restrict to only columns we need to reduce copying time
dat2 <- subset(dat, select = c('delay', 'origin', 'dest'))

# some overhead in copying 'dat2' to worker processes...
results <- foreach(destVal = destVals) %dopar% {
    sub <- subset(dat2, dest == destVal)
    summary(sub$delay)
}


results

closeCluster(cl)
mpi.quit()
```

### Example use of standard software: R on one node

If you just want to parallelize within a node:

```
srun -A co_stat -p savio2  -N 1 -t 30:0 --pty bash
module load r
R CMD BATCH --no-save parallel-one.R parallel-one.Rout &
```

Now here's the R code (see *parallel-one.R*) we're running:
```
library(doParallel)

nCores <- as.numeric(Sys.getenv('SLURM_CPUS_ON_NODE'))
registerDoParallel(nCores)

dat <- read.csv('/global/scratch/paciorek/bayArea.csv', header = FALSE,
                stringsAsFactors = FALSE)
names(dat)[16:18] <- c('delay', 'origin', 'dest')
table(dat$dest)

destVals <- unique(dat$dest)

results <- foreach(destVal = destVals) %dopar% {
    sub <- subset(dat, dest == destVal)
    summary(sub$delay)
}

results
```

# Example of hybrid parallelization with R using threaded linear algebra

If you have parallel R code (e.g., with foreach + doMPI or foreach + doSNOW) for which the computational tasks use linear algebra, you can also use a hybrid parallelization approach as outlined here. Note that the example file `parallel-multi-linalg.R` does not exist so this is just a template.

```
#!/bin/bash
# Job name:
#SBATCH --job-name=test
#
# Account:
#SBATCH --account=co_stat
#
# Partition:
#SBATCH --partition=savio2
#
# Number of tasks (2 nodes' worth)
#SBATCH --ntasks=12
#
# Processors per task:
#SBATCH --cpus-per-task=4
#
# Wall clock limit:
#SBATCH --time=04:00:00
#
module load r
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
mpirun R CMD BATCH --no-save parallel-multi-linalg.R parallel-multi-linalg.Rout &
```


# High-throughput computing
 
You may have many serial jobs to run. It may be more cost-effective to collect those jobs together and run them across multiple cores on one or more nodes.

Here are some options:

 - *ht_helper* (see next slide)
 - various forms of easy parallelization in Python and R 
     - some description in this document  
     - Chris Paciorek's tutorials on using [single-node parallelism](https://github.com/berkeley-scf/tutorial-parallel-basics) and [multiple-node parallelism](https://github.com/berkeley-scf/tutorial-parallel-distributed) in Python, R, and MATLAB

# ht_helper
 
The basic idea of ht_helper is to start up a single job and within that job to cycle through all of your computational tasks. 

This has a few benefits

 - uses all the cores on node even if each computational task is serial or only needs a few cores
 - systematically processes many computational tasks as a single job for ease of management
 - avoids overloading the scheduler with thousands of jobs as the scheduler is not designed to handle that load

More details are given in [the Savio tip on "How to run High-Throughput Computing ..."](http://research-it.berkeley.edu/services/high-performance-computing/tips-using-brc-savio-cluster)

# ht_helper example

To use *ht_helper.sh* we need a *taskfile* with one line per task. Generally one would programmatically generate this file, as I've done with *generate_taskfile.py*.

```
python < generate_taskfile.py
head taskfile
```

We can see that each line is uniquely identified by a different id, which is passed into the Python code file, *compute.py*.

Finally, we can look at the Python code file to see how each individual task is done. We write the output for each task to a separate file (as a simple way to avoid collisions in writing to a single output file; see below for an alternative) and then we can post-process the files to collect our results. 

To run our job, we submit *job_ht.sh*.

Here's how we might post-process in this simple situation:
```
cat exp_output1/* >> exp_output1_final
```

If you'd like to have all the tasks write to a common file, you'll want to lock the file while each file is writing to it. See *lock_example.py* for one way to do this.

# How to get additional help

 - For technical issues and questions about using Savio: 
    - brc-hpc-help@berkeley.edu
 - For questions about computing resources in general, including cloud computing: 
    - brc@berkeley.edu
 - For questions about data management (including HIPAA-protected data): 
    - researchdata@berkeley.edu


# Wrap-up

- Upcoming events
    - BRC/D-Lab Cloud Working Group (Track 1) every other Thursday in 356 Barrows
        - next session: Thursday Sep. 29 @ 4pm: RStudio and Jupyter Notebooks using Docker on Google Compute Engine
    - BRC Cloud Working Group (Track 2): Research Computing & Data Architecture + Advanced CyberInfrastructure
    - BRC Cloud Working Group (Track 3): Cloud Architecture & Infrastructure (UC-wide AWS User group)
        - next session: Wednesday Oct. 19 @ 2 pm

- Please help us justify the campus investment in Savio (and keep it available in the future) by [telling us how BRC impacts your research](https://docs.google.com/a/berkeley.edu/forms/d/e/1FAIpQLSdqhh2A77-l8N3eOcOzrH508UKfhIvPn8h5gLDUJ9XrRLvA5Q/viewform), e.g., through
    - publications about research supported by BRC
    - grants for research that will be supported by BRC resources or consulting
    - recruitment or retention cases in which BRC resources/services play a role
    - classes that will be supported by the BRC program

- Please fill out an evaluation form



