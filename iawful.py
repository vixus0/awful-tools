
"""
awftools
========

A set of routines designed for interactive use. 

:Example:

    >>> import awftools
    >>> awftools.init(nprocs=2) # initialise a 2-processor queue.
    >>> awftools.qsub("sleep 20") # will run 'sleep 20' in the current directory.
    >>> awftools.qsub("prog",nprocs=2,directory="~/path/to/directory",
    ...     combine_out_err=True)
    # will run 'prog' in the speficied directory. Prog will use up both processors
    # in the queue.
    # Both stdout and stderr will be saved to a file prog.out.
    >>> awftools.qstat_pretty() # Readable list of current jobs.
       Job     Status     Start     Finish
    =========================================
       sleep1  Running  10:00:00   
       prog1   Queuing

"""

import mdrunr
import ioutils

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


def qsub(cmd, name=None, nprocs=1, directory=None,combine_out_err=False):
    """
    Submit a job.

    :Parameters:
        - `cmd` : commant passed to the shell to run this job.
        - `name` : job name [default : first word of 'cmd' and job number]
        - `nprocs` : number of processors this job uses
            [default : 1].
        - `directory` : directory in which to run this job.
            [default : current directory].
        - `combine_out_err` : job error is saved to the same file
            as job output.
    """
    if name is None:
        name = _get_default_name(cmd,GetQueue.get_queue())
    job = mdrunr.Mdjob(name,cmd,nprocs,mpi_mode=False,directory=directory,
            combine_out_err=combine_out_err)
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
    jobs_dict = qstat() # { Mdjob : JobStatus }

    # Get the length of the longest job name to calculate width of column
    longest_job_name = max((len(job.name) for job in jobs_dict.iterkeys()))
    if longest_job_name > 50: # truncate at 50 chars max.
        longest_job_name = 50 

    # formats 
    time_format = "%X" # locale-dependent time representation.
    line_format =  "{0:>%is} {1:>12s} {2:>10s} {3:^10s}"%longest_job_name

    # Print the header.
    header = line_format.format("Job", "Status", "Start", "Finish") # title
    print header
    print "="*len(header) # underline title

    # Print each jobs.
    for job, job_status in jobs_dict.iteritems():
        start_time_str = ioutils.format_time_if_defined(
                time_format, job_status.start_time)
        finish_time_str = ioutils.format_time_if_defined(
                time_format, job_status.finish_time)
        job_string = line_format.format(
                job.name[:50],job_status.status,start_time_str,finish_time_str)
        print job_string

def _get_default_name(job_cmd, queue):
    first_word = job_cmd.split(" ",1)[0]
    number = sum(1 for job in queue.job_status_dict.iterkeys() 
            if job.name.upper().startswith(first_word.upper()))+1
    return first_word+str(number)

    
