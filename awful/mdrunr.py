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
import keyqueue
import logging
import os

import config

logging.basicConfig(filename="mdrunr.log",level=logging.DEBUG)
# To also log to stdout:
#logging.getLogger("").addHandler(logging.StreamHandler())


class Mdjob :
    """Defines a job to run."""

    def __init__(self, name, args, nprocs, mpi_mode=True, directory=None, 
            combine_out_err=False):
        """Create a job.
  
        :Parameters:
            - `name` : Job identifier.
            - `args` : command to run this job.
            - `nprocs` : number of processors this job will use.
            - `mpi_mode` : [default: True] If True, this job is
                run using 'mpiexec -n <nprocs> <args>'
            - `directory` : absolute path to the directory this job should run in.
                [default : current directory]
            - `combine_out_err` : if True, both the job's stdout and stderr will
                be sent to the 'name.out'. If False, stdout is sent to 'name.out'
                and stderr to 'name.err'. [default : False].

        :Methods:
            - constructor (defines the job).
            - `enqueue` : to be called when the job is added to a queue.
            - `run` : runs the job.
        """
        self.name = name
        self.args = args
        self.nprocs = nprocs
        self.mpi_mode = mpi_mode
        self.status = JobStatus()
        if directory is not None:
            self.directory = os.path.abspath(
                    os.path.expanduser(os.path.expandvars(directory)))
        else:
            self.directory = os.getcwd()
        self.combine_out_err = combine_out_err
        self.stdout_name = config.STDOUT_FILE.format(job_name=self.name)
        if not combine_out_err:
            self.stderr_name = config.STDERR_FILE.format(job_name=self.name)

    def enqueue(self):
        self.status.set_queuing()

    def run(self):
        self.status.set_starting()
        current_directory = os.getcwd() # save current directory.
        os.chdir(self.directory)
        self.stdout_file = open(self.stdout_name,config.STDOUT_MODE)
        if self.combine_out_err:
            self.stderr_file = self.stdout_file
        else:
            self.stderr_file = open(self.stderr_name,config.STDERR_MODE)
        if self.mpi_mode: 
            md_job = "mpiexec -n "+ str(self.nprocs) + " " + self.args
        else: 
            md_job = self.args
        sp.call(md_job, shell=True,
                stdout=self.stdout_file,stderr=self.stderr_file)
        os.chdir(current_directory) # return to previous directory.
        self.status.set_finished()

    def __repr__(self):
        return str(self.name) + str(self.status)


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

    This class encapsulates status information for a particular
    job object. 

    :Methods:
        - `set_queuing` : should be called when a job is 
            added to a queue.
        - `set_starting` : should be called when a job is 
            starting.
        - `set_finished` : should be called when a job is 
            finished.
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

    def __repr__(self):
        repr_string = "("+str(self.status)
        try:
            repr_string += ", "+time.strftime("%c",self.start_time)
        except TypeError: # start time is None (job is queuing)
            pass
        try:
            repr_string += ", "+time.strftime("%c",self.finish_time)
        except TypeError: # finish time is None (job is queuing/running)
            pass
        repr_string += ")"
        return repr_string


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
        self.queue._finish_job(self.job)


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
            - `todo_queue` : Threadsafe KeyQueue. List of { job_name : job }
                of jobs that still need to be done.
            - `running_or_done_queue` : Threadsafe KeyQueue. List of { job_name : job }
                of jobs that are either running, complete or deleted.
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
        self.todo_queue = keyqueue.KeyQueue()
        self.running_or_done_queue = keyqueue.KeyQueue()
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
        logging.debug("Job added : "+job.name)
        job.enqueue()
        self.todo_queue.put( (job.name, job) )

    def list_jobs(self):
        """
        List jobs in the queue.
        """
        with self.running_or_done_queue.locked():
            with self.todo_queue.locked():
                return self.running_or_done_queue.values() +\
                        self.todo_queue.values()

    def _start_job(self, job):
        self.free_cores -= job.nprocs
        runner = Runner(job, self)
        logging.debug("Thread spawned to run job : "+job.name)
        runner.daemon = True
        runner.start()

    def _finish_job(self, job):
        self.free_cores += job.nprocs

    def _start_next_job_when_possible(self):
        with self.running_or_done_queue.locked():
            with self.todo_queue.locked():
                # peek at next job without removing it from the queue.
                try:
                    next_job = self.todo_queue.values()[0] 
                except IndexError: # queue empty
                    pass
                else:
                    if next_job.nprocs <= self.free_cores:
                        # Next job can run...
                        logging.debug("Starting job : "+next_job.name)
                        job_name, job = self.todo_queue.get()
                        self.running_or_done_queue.put((job_name,job))
                        assert job_name == next_job.name # should always be true.
                        self._start_job(next_job)

    def start(self):
        """Initialise the queue."""
        logging.debug("Queue starting...")
        while True:
            try:
                self._start_next_job_when_possible()
                time.sleep(1)
            except KeyboardInterrupt:
                raise
                import sys ; sys.exit()


