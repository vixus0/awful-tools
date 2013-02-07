
Usage
=====

There are two ways to use "awful" to manage a job queue:

 * Using a python shell.
 * From the system shell (not implemented).


Python shell interface
----------------------

The following code snippet should get you started:

    >>> import iawful # interactive-awful
    # start the queue, declaring it has two processors available.
    >>> iawful.init(2) 
    >>> iawful.qsub("sleep 20", name="boring-job", nprocs=2, directory="~")
    # Submit a job. The first argument is the command line to run
    # the job. Tell the queue this job will use two processors.
    # Tell the queue to switch to "~" before running the job.
    >>> iawful.qstat_pretty() # print the currently queued jobs.


Notes
=====

Vaguely relevant information is logged to "mdrunr.log" in the directory in which the queue is initiated.

The stderr file for the jobs is in `/tmp/mdrunr.log`.
