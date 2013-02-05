
Developpers documentation
=========================

There are currently three modules:

* `mdrunr` defines the basic queue class `Mdrunr`, and the basic job class `Mdjob`.
* `server` provides tools to wrap `Mdrunr` in a Pyro server, so that the queue can be accessed by other processes.
* `client` provides utilititeis for connecting to that queue.
