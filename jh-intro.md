% Savio Jupyterhub training: JupyterHub on the Berkeley Savio high-performance computing cluster
% March 8, 2017
% Chris Paciorek and Maurice Manning


# Introduction

We'll do this mostly as a demonstration. I encourage you to login to your account and try out the various examples yourself as we go through them.

The first half of this material is based on the Savio JupyterHub documention we have prepared and continue to prepare, available at [http://research-it.berkeley.edu/services/high-performance-computing/XXXX](http://research-it.berkeley.edu/services/high-performance-computing/XXXX).

The materials for this tutorial are available using git at [https://github.com/ucberkeley/savio-training-jupyterhub-2017](https://github.com/ucberkeley/savio-training-jupyterhub-2017) or simply as a [zip file](https://github.com/ucberkeley/savio-training-jupyterhub-2017/archive/master.zip).

These *jh-intro.html* and *jh-intro_slides.html* files were created from *jh-intro.md* by running `make all` (see *Makefile* for details on how that creates the html files).

You can find the material from previous trainings at:
 - Introduction to Savio (August 2016): [zip file](https://github.com/ucberkeley/savio-training-intro-2017/archive/master.zip) 
 - Parallelization on Savio (September 2017): [zip file](https://github.com/ucberkeley/savio-training-parallel-2017/archive/master.zip)


# Outline

This training session will cover the following topics:

 - Review of Jupyter/IPython notebook basics
 - Introduction to Jupyterhub on Savio
      - Logging on and getting started
      - Managing notebooks
 - Parallel processing using IPython Notebooks on Savio
      - Setting up a basic IPython cluster on one node
      - Customizing your IPython cluster setup
      - Setting up an IPython cluster to run on multiple nodes
 - Integration with Box
      - Use case(s) for Box integration
      - Installing the Box SDK in your kernel of choice
      - Authentication
      - Creating a client id 
      - Bootstrap process and notebook
      - Notebook authentication boilerplate code
      - Retrieving data from Box
      - Pushing data to Box
      - Modularization

# Review of Jupyter/IPython notebook basics

We'll review basic usage of a notebook using *notebook-example.ipynb*.

I've installed the Anaconda distribution of Python (actually a reduced form version called Miniconda) on my laptop, from <https://conda.io/miniconda.html> and then from the command line installed Jupyter: 

```
conda install jupyter
```

which also installs IPython. Then I can start a Jupyter notebook server and run notebooks by simply invoking `jupyter notebook` or `jupyter notebook notebook-example.ipynb`. 

# Introduction to Jupyterhub on Savio: logging on

We can run notebooks on Savio, using a variety of partitions/nodes. 

We need to login via a browser from <https://ln000.brc.berkeley.edu>, authenticating using our usual PIN and one-time password (from Google Authenticator). 



We can choose from:

 - Local server 
    - testing
    - controlling multi-node parallel clusters)
 - Savio (1 node) 
    - for parallel computation
 - Savio2 (1 node) 
    - for parallel computation
 - Savio2_HTC (1 cpu)
    - for serial computation
 - Let us know if you need other configurations (e.g., GPU nodes, big memory nodes, etc.)

Then we can immediately start working on our example notebook.

We could also start a terminal and get a view on the filesystem and on the processes running on the node. 

# Introduction to Jupyterhub on Savio: managing notebooks

The key navigation points in your Jupyter browser session are:

 - `jupyter` banner: to navigate within your session (to the file manager and between processes)
 - `Running -> shutdown`: to terminate an individual process
 - `Logout`: to logout of the session but NOT terminate your notebook/terminal processes (running processes on compute nodes will still incur charges)
 - `Control Panel -> Stop My Server`: to terminate all processes and your server

# IPython clusters: one node cluster -- setup

One can do parallel processing in a variety of ways in Python. Here we'll cover IPython parallel clusters. We'll start with a one node cluster. 

Such clusters (except for basic testing) should be run under the `Savio - 1 node` or `Savio2 - 1 node` job profile.

 - Invoke 
```/global/software/sl-6.x86_64/modules/langs/python/3.5.1/bin/ipcluster nbextension enable --user``` 
    from a terminal (either logging in via SSH or in a Jupyter terminal session).
 - You should see that the `Clusters` tab is now `IPython Clusters` on the main Jupyter page. If not, then stop and restart your server through `Control Panel`.

# IPython clusters: one node cluster -- running

 - Start a server under the `Savio - 1 node` or `Savio2 - 1 node` job profile.
 - Under `IPython Clusters`, select the number of engines (i.e., cores, cpus) and `Start` under the `default` profile.
 - Start or go to a running notebook. 
 - This code should connect you to your cluster:

```
import IPython.parallel as ipp 
rc = ipp.Client(profile='default', cluster_id='')
```

The file *parallel-example.py*  has some examples of some basic usage.

*I may want to convert that to an ipynb once have clarity from Yong on issues with running the code*

# IPython clusters: customization -- setup

Suppose you want to run your workers in a different Savio partition, change the time limit, or use more than one node for your computation.

In that case you need to set up a custom cluster profile. This involves setting values for SLURM options in such a way that IPython can submit the appropriate job to SLURM. 

Here are the steps (also documented on the Savio JupyterHub page):

 - In a terminal (either from JupyterHub or not), enter:
```
PROFILENAME=myNewProfile
/global/software/sl-6.x86_64/modules/langs/python/3.5.1/bin/ipython profile create --parallel --profile=${PROFILENAME}
```
 - Now go to the newly created directory for the profile:
```
cd $HOME/.ipython/profile_${PROFILENAME}
```
 - Add the following to *ipcontroller_config.py*:
```
cat >> ipcontroller_config.py << EOF
import netifaces
c.IPControllerApp.location = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
c.HubFactory.ip = '*'
EOF
```
 - Now modify the options in *custom_profile_code.py* and append it to *ipcluster_config.py*.
```
cat custom_profile_code.py >> ipcluster_config.py
```

# IPython clusters: customization -- using

Now we should be able to start a cluster using this profile under the *IPython Clusters* tab, as follows.

Select the number of engines corresponding to the number of tasks you specified in ipcluster_config.py (48 in this case).

Then start a Notebook and connect to the cluster.

For example, we use the same code as we did before, but needing to specify the name of the cluster, which is set to be *paciorek* in *custom_profile_code.py*.

```
import IPython.parallel as ipp 
rc = ipp.Client(profile='myNewProfile', cluster_id='')
rc.ids
```

# How to get additional help

 - For technical issues and questions about using Savio: 
    - brc-hpc-help@berkeley.edu
 - For questions about computing resources in general, including cloud computing: 
    - brc@berkeley.edu
 - For questions about data management (including HIPAA-protected data): 
    - researchdata@berkeley.edu

# How to help us

- Please help us justify the campus investment in Savio (and keep it available in the future) by [telling us how BRC impacts your research](https://docs.google.com/a/berkeley.edu/forms/d/e/1FAIpQLSdqhh2A77-l8N3eOcOzrH508UKfhIvPn8h5gLDUJ9XrRLvA5Q/viewform), e.g., through
    - publications about research supported by BRC
    - grants for research that will be supported by BRC resources or consulting
    - recruitment or retention cases in which BRC resources/services play a role
    - classes that will be supported by the BRC program

- Please fill out an evaluation form



