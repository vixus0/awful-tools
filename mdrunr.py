#!/usr/bin/env python

""" 
mdrunr
======

Provide a queuing system.

Author: Anshul Sirur
"""

import time
import multiprocessing as mp
import subprocess as sp
import threading as thr
import Queue as qu
import logging
import collections
import os

logging.basicConfig(filename="mdrunr.log",level=logging.DEBUG)
# To also log to stdout:
#logging.getLogger("").addHandler(logging.StreamHandler())

fnull=open("/dev/null", "w")
flog=open("/tmp/mdrunr.log", "w")


class Mdjob :
    """Defines a job to run."""

    def __init__(self, name, args, nprocs, mpi_mode=True, directory=None):
        """Create a job.
  
        :Parameters:
            - `name` : Job identifier.
            - `args` : command to run this job.
            - `nprocs` : number of processors this job will use.
            - `mpi_mode` : [default: True] If True, this job is
                run using 'mpiexec -n <nprocs> <args>'
            - `directory` : absolute path to the directory this job should run in.
                [default : current directory]
        """
        self.name = name
        self.args = args
        self.nprocs = nprocs
        self.mpi_mode = mpi_mode
        if directory is not None:
            self.directory = os.path.abspath(os.path.expanduser(os.path.expandvars(directory)))
        else:
            self.directory = os.getcwd()

    def run(self):
        current_directory = os.getcwd() # save current directory.
        os.chdir(self.directory)
        if self.mpi_mode: 
            md_job = "mpiexec -n "+ str(self.nprocs) + " " + self.args
        else: 
            md_job = self.args
        sp.call(md_job, stdout=fnull, stderr=flog, shell=True)
        os.chdir(current_directory) # return to previous directory.


class JobStatus(object):
    """
    Keep a record of the current status of a job.

    :Attributes:
        - `status` : whether a job is currently in the queue,
            running or queuing.
        - `start_time` : time object indicating when the job
            started, or None.
        - `finish_time` : time object indicating when the job
            finished, or None.
    """

    # job status flags.
    QUEUING = "Queuing"
    RUNNING = "Running"
    FINISHED = "Finished"

    def __init__(self):
        self.status = None
        self.start_time = None
        self.finish_time = None

    def set_queuing(self):
        self.status = JobStatus.QUEUING

    def set_starting(self):
        self.status = JobStatus.RUNNING
        self.start_time = time.gmtime()

    def set_finished(self):
        self.finish_time = time.gmtime()
        self.status = JobStatus.FINISHED


class Runner(thr.Thread):
    def __init__(self, job, queue):
        logging.debug("Thread spawned.")
        self.job = job
        self.queue = queue
        thr.Thread.__init__(self)

    def run(self):
        logging.debug("Starting job: "+self.job.name)
        self.job.run()
        logging.debug("Done: "+self.job.name)
        self.queue._finish_job(self,self.job)


class Mdrunr(object):
    """Sets up and runs a queue."""

    def __init__(self, md_args_list=None, np_tot=None):
        """Initialise the queue.

        :Parameters:
            - `md_args_list` : MdJob instances describing the jobs.
                [default: empty tuple].
            - `np_tot` : total number of processors to use 
                [default: all cores on this computer].

        :Attributes:
            - `queue` : Threadsafe queue. Jobs are always run in the 
                order in which they are in the queue.
            - `job_status_dict` : { job : job_status } dictionary,
                kept in the same order as `queue`.
                Used to keep information about the jobs.
            - `np_tot` : total number of cores the queue has to play with.
                Set at instantiation.
            - `free_cores` : the number of cores currently available to run
                jobs. This is always `np_tot` - `job.nprocs` for all `job`s
                currently running.
            - `monitor` : thread in charge of monitoring whether there
                is enough free CPU's to run the next job. 

        :Methods:
            - `add_job` : add a job to the queue.
            - `list_jobs` : list the current jobs.
        """
        if np_tot is None:
            self.np_tot   = mp.cpu_count()
        else:
            self.np_tot = np_tot

        jobs = md_args_list if md_args_list is not None else tuple()
        self.queue = qu.Queue()
        self.job_status_dict = collections.OrderedDict()
        self.free_cores = self.np_tot
        for x in jobs:
            self.add_job(x)
        monitor = thr.Thread(target=self.start)
        monitor.daemon = True
        monitor.start()

    def add_job(self, job):
        """
        Add a job to the queue.
        """
        self.job_status_dict[job] = JobStatus()
        self.job_status_dict[job].set_queuing()
        self.queue.put(job)

    def list_jobs(self):
        """
        List jobs in the queue.
        """
        return self.job_status_dict

    def _start_job(self, job):
        self.job_status_dict[job].set_starting()
        self.free_cores -= job.nprocs
        runner = Runner(job,self)
        runner.daemon = True
        runner.start()

    def _finish_job(self, runner, job):
        self.job_status_dict[job].set_finished()
        self.free_cores += job.nprocs

    def _start_next_job_when_possible(self):
        job = self.queue.get()
        logging.debug("Next job queued: "+job.name)
        while job.nprocs > self.free_cores:
            time.sleep(1)
        self._start_job(job)

    def start(self):
        """Initialise the queue."""
        logging.debug("Queue starting...")
        while True:
            try:
                self._start_next_job_when_possible()
            except KeyboardInterrupt:
                raise
                import sys ; sys.exit()


