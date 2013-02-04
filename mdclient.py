
import subprocess as sp
import Pyro.core
import os

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


def _load_queue_uri():
    with open("/tmp/awfuld_uri.tmp") as f:
        uri = f.readline().strip()
    return uri

def load_queue():
    """
    Returns a handle to the queue server.
    """
    return Pyro.core.getProxyForURI(_load_queue_uri())

