
import unittest
import os
import sys
import mock
import subprocess
import time

sys.path.insert(0,os.path.abspath("../.."))

import awful.iawful as iawful

class TestIAwful(unittest.TestCase):
    """
    Test suite for iawful interactive module.
    """

    def setUp(self):
        iawful.init(2)
        self.queue = iawful.GetQueue.get_queue()

    def test_qsub(self):
        self.queue.add_job = mock.Mock()
        iawful.qsub("sleep 5")
        assert self.queue.add_job.call_count == 1
        args, kwargs = self.queue.add_job.call_args_list[0] # called with ... 
        assert len(args) == 1 # a single argument
        assert len(kwargs) == 0
        job = args[0]
        assert job.args == "sleep 5"
        assert job.nprocs == 1

    def test_qstat(self):
        subprocess = mock.Mock() # we don't actually want anything to run...
        os.open = mock.Mock()    # ... or to leave lots of files around.
        iawful.qsub("sleep 1",name="job-1")
        iawful.qsub("sleep 2",name="job-2")
        job_list = iawful.qstat()
        assert len(job_list) == 2
        job1, job2 = job_list
        assert job1.name == "job-1"
        assert job2.name == "job-2"

    def test_qstat_pretty(self):
        subprocess = mock.Mock() # we don't actually want anything to run...
        os.open = mock.Mock()    # ... or to leave lots of files around.
        iawful.qsub("sleep 1",name="job-1")
        iawful.qsub("sleep 2",name="job-2")
        print "\nThe following should look vaguely like a table: "
        print
        iawful.qstat_pretty()
        print "\nWaiting for jobs to run..."
        time.sleep(5)
        print "\nThe following should look vaguely like a table: "
        print
        iawful.qstat_pretty()
        print



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIAwful)
    unittest.TextTestRunner(verbosity=2).run(suite)
