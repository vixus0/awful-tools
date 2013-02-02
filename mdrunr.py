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

import sys, time
import multiprocessing as mp
import threading as thr
import Queue as qu
import subprocess as sp

fnull=open("/dev/null", "w")
flog=open("/tmp/mdrunr.log", "w")

class Mdjob :
  """Defines a job to run."""

  def __init__(self, name, args, mpi_mode=True):
    """Create a job.

    Arguments are name and an argument list (use shlex.split!).
    """
    self.name = name
    self.args = args
    self.mpi_mode = mpi_mode

  def run(self,np_per):
    if self.mpi_mode: 
      md_job = ["mpiexec", "-n", np_per] + self.args
    else: 
      md_job = self.args
    sp.call(md_job, stdout=fnull, stderr=flog)

class runner (thr.Thread):
  def __init__(self, queue, np_per,mpi_mode=True):
    thr.Thread.__init__(self)
    self.my_queue = queue
    self.np_per = np_per
    self.mpi_mode = mpi_mode

  def run(self):
    while True:
      try:
        my_job = self.my_queue.get(True,2)
      except qu.Empty:
        return
      else:
        if my_job:
          print "Starting job: ", my_job.name
          my_job.run(self.np_per)
          print "Done: ", my_job.name
          time.sleep(.5)
          self.my_queue.task_done()


class Mdrunr :
  """Sets up and runs a queue."""

  def __init__(self, md_args_list, np_per, np_tot=None):
    """Initialise the queue.

    :Parameters:
        - `md_args_list` : MdJob instances describing the jobs.
        - `np_per` : number of processes to use per job.
        - `np_tot` : total number of processors to use.
    """
    if np_tot is None:
        self.np_tot   = mp.cpu_count()
    else:
        self.np_tot = np_tot

    if np_per > self.np_tot:
      print "You can't specify more than %d processors per job!"%(self.np_tot)
      sys.exit(1)

    self.np_per   = np_per
    self.nthr     = self.np_tot / np_per
    self.jobs     = md_args_list
    self.queue    = qu.Queue(maxsize=len(md_args_list))

  def start(self):
    """Start submitting jobs from the queue."""
    try:

      for x in self.jobs:
        print "Added job: ", x.name
        self.queue.put(x)
      
      for i in range(self.nthr):
        t = runner(self.queue, self.np_per)
        t.daemon = True
        t.start()

      self.queue.join()
      print "done!"
    except (KeyboardInterrupt, SystemExit):
      print "Force quit!"


