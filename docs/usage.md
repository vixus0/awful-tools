
Usage
=====

There are two ways to use "awful" to manage a job queue:

 * easy way: open an interactive python shell, define your jobs and submit them, all from within the shell.  The queue dies when the shell exits (though your job may not get killed).
 * hard way: start a queuing server and submit jobs when you want. 
The queue runs as a daemon and will carry on living until the it is explicitly killed. 


Easy way
--------

Define your jobs as follows:

    >>> import mdrunr as mdr
    >>> job1 = mdr.Mdjob("job-1","ls",nprocs=1,mpi_mode=False)
    >>> job2 = mdr.Mdjob("job-2","whoami",nprocs=2,mpi_mode=False,directory="~/directory")

Then just start the jobs:

    >>> q = mdr.Mdrunr((job1,job2),np_tot=2)

Note that control is immediately returned to the shell. The queue runs in the background. You can keep on submitting jobs to the queue:

    >>> job3 = mdr.Mdjob("job-3","apt-get moo", nprocs=1,mpi_mode=False)
    >>> q.add_job(job3)

You can list the jobs using the `q.list_jobs()` function. This returns an ordered dictionary with `Mdjob` instances as keys and status information as values:

    >>> jobs_status = q.list_jobs()
    >>> for job, status in jobs_status.iteritems():
    ...     print job.name, status["status"] 
    job-1 Finished
    job-2 Finished
    job-3 Finished


Hard way
--------

Start the queuing server using 

    $ python mdrunr.py &

Then, in an interactive python shell: 

    >>> import client 
    >>> qserver = client.load_queue() # qserver is a reference to the queuing server.

`qserver` has exactly has the same methods as `q` in the "Easy way" section above. You can therefore submit jobs as before:

    >>> import mdrunr as mdr
    >>> job3 = mdr.Mdjob("job-3","apt-get moo", nprocs=1,mpi_mode=False)
    >>> q.add_job(job3)

You can also list jobs in a similar manner.

The advantage of using this method is that you can exit the python shell without killing the underlying server. The disadvantage is that everything is likely to crash and burn in an orgy of fire and death.


Defining jobs
=============

Jobs are defined using the `Mdjob` function in the `mdrunr` module. The function signature is as follows:

    Mdjob(name, args, nprocs, mpi_mode, directory)

- `name` : String to identify job. Should be unique.
- `args` : The command line string to execute the job. This just gets passed directly
	 to the shell.
	 Valid args strings include `ls`, `rm -rf *`, `find ~ -name "ali_babas_treasure_trove"`, etc.
- `nprocs` : How many cores this job will occupy. If the queue is launched with 4 processors, it will run a single job with `nprocs = 4`, or two jobs with `nprocs = 2`, concurrently, or four jobs with `nprocs = 1`, concurrently.
- `mpi_mode` : If True (default), then the `args` string is prefixed with `mpiexec -n <nprocs>` when passed to the shell. Thus, `args` should just contain the arguments to the MPI job.
- `directory` : move to this directory before running the job.
 

Notes
=====

Vaguely relevant information is logged to "mdrunr.log" in the directory in which the queue is initiated.
