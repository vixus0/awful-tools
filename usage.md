
Usage
=====

Summary
-------

Start the queuing server using 

    $ python mdrunr.py &

Then, in an interactive python shell: 

    >>> import mdclient as mdc
    >>> qserver = mdc.load_queue() # qserver is a reference to the queuing server.

To submit jobs to the queue, instantiate the jobs as follows:

    >>> job1 = mdc.Mdjob("job-1","ls",nprocs=1,mpi_mode=False)
    # creates a job with name "job-1", where the command to run the job
    # is "ls", and which will require 1 processor.

Then, submit the job to the queue-server:

    >>> qserver.add_job(job1)

The queuing server can currently only be closed by killing it. Note that killing it may not kill jobs which are currently active.

The jobs currently queued can be listed using:

    >>> qserver.list_jobs()
