#!/usr/bin/env python

""" 
mdrunr
======

Provide a queuing server.

Author: Anshul Sirur
"""

import time
import multiprocessing as mp
import threading as thr
import Queue as qu
import logging
import Pyro.core
import Pyro.naming

logging.basicConfig(filename="mdrunr.log",level=logging.DEBUG)
# To also log to stdout:
#logging.getLogger("").addHandler(logging.StreamHandler())


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
        self.queue.finish_job(self,self.job)


class Mdrunr(Pyro.core.ObjBase):
    """Sets up and runs a queue."""

    def __init__(self, md_args_list=None, np_tot=None):
        """Initialise the queue.

        :Parameters:
            - `md_args_list` : MdJob instances describing the jobs.
                [default: empty tuple].
            - `np_tot` : total number of processors to use 
                [default: all cores on this computer].
        """
        if np_tot is None:
            self.np_tot   = mp.cpu_count()
        else:
            self.np_tot = np_tot

        self.jobs     = md_args_list if not None else tuple()
        self.queue    = qu.Queue()
        self.free_cores = self.np_tot
        for x in self.jobs:
            self.add_job(x)
        Pyro.core.ObjBase.__init__(self)
        monitor = thr.Thread(target=self.start)
        monitor.daemon = True
        monitor.start()

    def add_job(self, job):
        self.queue.put(job)

    def finish_job(self, runner, job):
        self.free_cores += job.nprocs

    def start_next_job_when_possible(self):
        job = self.queue.get()
        logging.debug("Next job queued: "+job.name)
        while job.nprocs > self.free_cores:
          time.sleep(1)
        self.free_cores -= job.nprocs
        runner = Runner(job,self)
        runner.daemon = True
        runner.start()

    def start(self):
        """Start submitting jobs from the queue."""
        logging.debug("Queue starting...")
        while True:
            try:
                self.start_next_job_when_possible()
            except KeyboardInterrupt:
                raise
                import sys ; sys.exit()

    def echo(self):
        logging.debug("hello")
        print "hello"


def _save_uri(uri):
    with open("/tmp/awfuld_uri.tmp","w") as f:
        f.write(str(uri))


def start_server(args_list=None, np_tot=None):
    """
    Start the queue-ing server. 

    :Parameters:
        - `args_list` : list of jobs to run on the queuing server.
        - `np_tot` : number of processors to allocate.

    The queuing server can be accessed via a URI stored in 
    :file:`/tmp/awfuld_uri.tmp`.
    """
    q = Mdrunr(args_list, np_tot)
    daemon = Pyro.core.Daemon(host="127.0.0.1")
    uri = daemon.connect(q,name="awfuld")
    _save_uri(uri)
    daemon.requestLoop()


if __name__ == '__main__':
    start_server()

