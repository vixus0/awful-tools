
"""
awftools
========

A set of routines designed for interactive use. 

:Example:

    >>> import awftools
    >>> awftools.init(nprocs=2) # initialise a 2-processor queue.
    >>> awftools.qsub("sleep 20") # will run 'sleep 20' in the current directory.
    >>> awftools.qsub("prog",nprocs=2,directory="~/path/to/directory") 
    # will run 'prog' in the speficied directory. Prog will use up both processors
    # in the queue.
    >>> awftools.qstat_pretty()
    sleep1  Running
    prog    Queuing

"""

import mdrunr

class NoQueueDefined(Exception):
    """
    User requests a queue, but 'init' has not been run yet.
    """
    pass

class GetQueue(object):
    """
    Singleton to manage a queue.
    """
    queue = None

    @staticmethod
    def get_queue():
        if GetQueue.queue is None:
            raise NoQueueDefined("There is no currently defined queue. "
                    "Use start_queue() to start one.")
        else:
            return GetQueue.queue


def init(nprocs=None):
    """
    Start a queue with `nprocs` processors.
    """
    GetQueue.queue = mdrunr.Mdrunr(None, nprocs)


def qsub(cmd, name=None, nprocs=1, directory=None):
    """
    Submit a job.

    :Parameters:
        - `cmd` : commant passed to the shell to run this job.
        - `name` : job name [default : first word of 'cmd' and job number]
        - `nprocs` : number of processors this job uses
            [default : 1].
        - `directory` : directory in which to run this job.
            [default : current directory].
    """
    if name is None:
        name = _get_default_name(cmd,GetQueue.get_queue())
    job = mdrunr.Mdjob(name,cmd,nprocs,mpi_mode=False,directory=directory)
    GetQueue.get_queue().add_job(job)

def qstat():
    """
    Return a dictionary { job: job_status }.

    See also: qstat_pretty
    """
    return GetQueue.get_queue().list_jobs()

def qstat_pretty():
    """
    Print a nicely formatted list of jobs in the queue to screen.

    See also: qstat
    """
    for job, job_status in qstat().iteritems():
        print job.name, "  ", job_status["status"]

def _get_default_name(job_cmd, queue):
    first_word = job_cmd.split(" ",1)[0]
    number = sum(1 for job in queue.job_status_dict.iterkeys() 
            if job.name.upper().startswith(first_word.upper()))+1
    return first_word+str(number)

    
