
import Pyro.core

import mdrunr

class MdrunrServer(Pyro.core.ObjBase):
    """
    Wrap mdrunr.Mdrunr in a server. 

    This class takes an existing `Mdrunr` queue and wraps it in 
    a Pyro server. This allows other python instances to address
    the queue.

    All "public" methods of Mdrunr are supported. See :class:`Mdrunr`
    for details.

    :Params:
        - `queue` : Mdrunr instance to be wrapped.
    """
    def __init__(self,queue):
        self.queue = queue
        Pyro.core.ObjBase.__init__(self)

    def add_job(self, job):
        self.queue.add_job(job)

    def list_jobs(self):
        return self.queue.list_jobs()

    def echo(self):
        print "hello"


def _save_uri(uri):
    with open("/tmp/awfuld_uri.tmp","w") as f:
        f.write(str(uri))



def start_server(args_list=None, np_tot=None):
    """
    Initialise a queue, wrap it in a server and daemonize.

    :Parameters:
        - `args_list` : list of jobs to run on the queuing server.
        - `np_tot` : number of processors to allocate.

    The queuing server can be accessed via a URI stored in 
    :file:`/tmp/awfuld_uri.tmp`.
    """
    q = mdrunr.Mdrunr(args_list, np_tot)
    server = MdrunrServer(q)
    daemon = Pyro.core.Daemon(host="127.0.0.1")
    uri = daemon.connect(server,name="awfuld")
    _save_uri(uri)
    daemon.requestLoop()


if __name__ == '__main__':
    start_server()

