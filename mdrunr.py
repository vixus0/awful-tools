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

  def __init__(self, name, args):
    """Create a job.

    Arguments are name and an argument list (use shlex.split!).
    """
    self.name = name
    self.args = args

class runner (thr.Thread):
  def __init__(self, queue, np_per):
    thr.Thread.__init__(self)
    self.my_queue = queue
    self.np_per = np_per

  def run(self):
    while True:
      try:
        my_job = self.my_queue.get(True,2)
      except:
        return
      else:
        if my_job:
          md_job = ["mpiexec", "-n", `self.np_per`] + my_job.args
          print "Starting job: ", my_job.name
          sp.call(md_job, stdout=fnull, stderr=flog)
          time.sleep(.5)
          self.my_queue.task_done()


class Mdrunr :
  """Sets up and runs a queue."""

  def __init__(self, md_args_list, np_per):
    """Initialise the queue.

    Arguments are a list of Mdjobs and the number of processors per job.
    """
    self.np_tot   = mp.cpu_count()

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
      for i in range(self.nthr):
        t = runner(self.queue, self.np_per)
        t.daemon = True
        t.start()

      for x in self.jobs:
        print "Added job: ", x.name
        self.queue.put(x)
      
      print "Running..",
      while self.queue.empty() == False:
        time.sleep(1)
      print "done!"
    except (KeyboardInterrupt, SystemExit):
      print "Force quit!"

