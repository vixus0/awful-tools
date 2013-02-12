
"""
client
======

A set of tools for clients intending to address the queuing server.
"""

import Pyro.core

def _load_queue_uri():
    with open("/tmp/awfuld_uri.tmp") as f:
        uri = f.readline().strip()
    return uri

def load_queue():
    """
    Returns a handle to the queue server.
    """
    return Pyro.core.getProxyForURI(_load_queue_uri())

