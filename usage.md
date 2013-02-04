
Usage
=====

There are two ways to use "awful" to manage a job queue:

 * easy way: open an interactive python shell, define your jobs and submit them, all from within the shell.  The queue dies when the shell exits (though your job may not get killed).
 * hard way: start a queuing server and submit jobs when you want. 
The queue runs as a daemon and will carry on living until the it is explicitly killed. 


Easy way
--------

Define your jobs as follows:

    >>> import mdclient as mdc
    >>> import mdrunr as mdr
    >>> job1 = mdc.Mdjob("job-1","ls",nprocs=1,mpi_mode=False)
    >>> job2 = mdc.Mdjob("job-2","whoami",nprocs=2,mpi_mode=False)

Then just start the jobs:

    >>> q = mdr.Mdrunr((job1,job2),np_tot=2)

Note that control is immediately returned to the shell. The queue runs in the background. You can keep on submitting jobs to the queue:

    >>> job3 = mdc.Mdjob("job-3","apt-get moo", nprocs=1,mpi_mode=False)
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

    >>> import mdclient as mdc
    >>> qserver = mdc.load_queue() # qserver is a reference to the queuing server.

`qserver` has exactly has the same methods as `q` in the "Easy way" section above. You can therefore submit jobs as before:

    >>> job3 = mdc.Mdjob("job-3","apt-get moo", nprocs=1,mpi_mode=False)
    >>> q.add_job(job3)

You can also list jobs in a similar manner.

The advantage of using this method is that you can exit the python shell without killing the underlying server. The disadvantage is that everything is likely to crash and burn in an orgy of fire and death.


Notes
=====

There is currently no support for choosing directories when running jobs. Thus, if you want to run a job in some directory "/i/am/a/directory/", you should define your job as a "cd /i/am/a/directory && job".

Vaguely relevant information is logged to "mdrunr.log" in the directory in which the queue is initiated.
