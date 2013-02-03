#!/usr/bin/env python

""" Module for running multiple jobs on multiple processors.

This module allows simple, automatic queueing of MPI-enabled
applications, via mpiexec. So if you have a whole bunch of jobs
to run this will do them. Everything goes in the one queue at
the moment but in consecutive order, so think about the queue order!

class Mdjob: defines a job by name and by commandline argument list
class Mdrunr: the actual queueing system

Author: Anshul Sirur
"""

import time
import multiprocessing as mp
import threading as thr
import Queue as qu
import subprocess as sp

fnull=open("/dev/null", "w")
flog=open("/tmp/mdrunr.log", "w")

class Mdjob :
  """Defines a job to run."""

  def __init__(self, name, args, nprocs, mpi_mode=True):
    """Create a job.

    :Parameters:
        - `name` : Job identifier.
        - `args` : command to run this job.
        - `nprocs` : number of processors this job will use.
        - `mpi_mode` : [default: True] If True, this job is
            run using 'mpiexec -n <nprocs> <args>'
    """
    self.name = name
    self.args = args
    self.nprocs = nprocs
    self.mpi_mode = mpi_mode

  def run(self):
    if self.mpi_mode: 
      md_job = "mpiexec -n "+ str(self.nprocs) + " " + self.args
    else: 
      md_job = self.args
    sp.call(md_job, stdout=fnull, stderr=flog, shell=True)


class Runner(thr.Thread):
    def __init__(self, job, queue):
        print "Thread born."
        self.job = job
        self.queue = queue
        thr.Thread.__init__(self)

    def run(self):
        print "Starting job: ",self.job.name
        self.job.run()
        print "Done: ",self.job.name
        time.sleep(0.5)
        self.queue.finish_job(self,self.job)


class Mdrunr :
  """Sets up and runs a queue."""

  def __init__(self, md_args_list, np_tot=None):
    """Initialise the queue.

    :Parameters:
        - `md_args_list` : MdJob instances describing the jobs.
        - `np_tot` : total number of processors to use 
            [default: all cores on this computer].
    """
    if np_tot is None:
        self.np_tot   = mp.cpu_count()
    else:
        self.np_tot = np_tot

    self.jobs     = md_args_list
    self.queue    = qu.Queue(maxsize=len(md_args_list))
    self.free_cores = self.np_tot


  def finish_job(self, runner, job):
    self.free_cores += job.nprocs

  def start_next_job_when_possible(self):
      job = self.queue.get()
      print "Next job queued: ",job.name
      while job.nprocs > self.free_cores:
          time.sleep(1)
      self.free_cores -= job.nprocs
      runner = Runner(job,self)
      runner.daemon = True
      runner.start()

  def start(self):
    """Start submitting jobs from the queue."""
    #self.init_runners()
    for x in self.jobs:
        self.queue.put(x)
    while not self.queue.empty():
        self.start_next_job_when_possible()


