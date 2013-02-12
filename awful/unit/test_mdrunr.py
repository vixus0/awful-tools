
import unittest
import mock
import os
import sys
import subprocess
import time

sys.path.insert(0,os.path.abspath("../.."))

import awful.mdrunr as mdrunr

class TestMdjob(unittest.TestCase):
    """
    Basic testing of Mdjob instances.
    """
    def setUp(self):
        self.j1 = mdrunr.Mdjob("job-1", "./test_job", nprocs=1,mpi_mode=False)
        self.j2 = mdrunr.Mdjob("job-2", "sleep 20", nprocs=1,mpi_mode=True)
        self.j3 = mdrunr.Mdjob("job-3", "sleep 20", nprocs=1,mpi_mode=True,
                combine_out_err=True)
        self.j4 = mdrunr.Mdjob("job-4", "sleep 20", nprocs=1,mpi_mode=False,
                directory="test_dir")

    def test_constructor(self):
        assert self.j1.name == "job-1"
        assert self.j1.args == "./test_job"
        assert self.j4.directory == os.getcwd()+"/test_dir"
        assert self.j2.stdout_name == "job-2.out"
        assert self.j2.stderr_name == "job-2.err"
        assert self.j3.stdout_name == "job-3.out"
        assert self.j2.combine_out_err is False 
        assert self.j3.combine_out_err is True 

    def test_run_no_cd(self):
        subprocess.call = mock.Mock()
        self.j1.run()
        subprocess.call.assert_called_once_with(
                "./test_job", shell=True, stdout=self.j1.stdout_file,
                stderr=self.j1.stderr_file)
        assert self.j1.stdout_file.name == "job-1.out"
        assert self.j1.stderr_file.name == "job-1.err"

        subprocess.call = mock.Mock()
        self.j2.run()
        subprocess.call.assert_called_once_with(
                "mpiexec -n 1 sleep 20", shell=True, 
                stdout=self.j2.stdout_file,
                stderr=self.j2.stderr_file)
        assert self.j2.stdout_file.name == "job-2.out"
        assert self.j2.stderr_file.name == "job-2.err"
        assert self.j2.status.status == mdrunr.JobStatus.FINISHED

    def test_run_with_cd(self):
        subprocess.call = mock.Mock()
        os.chdir = mock.Mock()

        self.j4.run()
        subprocess.call.assert_called_once_with(
                "sleep 20", shell=True, stdout=self.j4.stdout_file,
                stderr=self.j4.stderr_file)
        assert os.chdir.call_args_list == [ 
                ( (os.getcwd()+"/test_dir",), {} ),
                ( (os.getcwd(),), {} ) ]


class TestMdrunr(unittest.TestCase):
    """
    Basic testing of Mdrunr instances.
    """
    def setUp(self):
        self.j1 = mdrunr.Mdjob("job-1","./test_job", nprocs=1,mpi_mode=False)
        self.j2 = mdrunr.Mdjob("job-2","sleep 20", nprocs=1,mpi_mode=False)
        self.j3 = mdrunr.Mdjob("job-3","sleep 20", nprocs=2,mpi_mode=False)
        self.j4 = mdrunr.Mdjob("job-4","sleep 20", nprocs=4,mpi_mode=False)
        self.j1.run = mock.Mock()
        self.j2.run = mock.Mock()
        self.j3.run = mock.Mock()
        self.j4.run = mock.Mock()

    def test_queue(self):
        q = mdrunr.Mdrunr(np_tot=2)
        q.add_job(self.j1)
        q.add_job(self.j2)
        q.add_job(self.j3)
        q.add_job(self.j4)
        time.sleep(5) # give time for the queue to process all the jobs.
        assert self.j1.run.call_count == 1
        assert self.j2.run.call_count == 1
        assert self.j3.run.call_count == 1
        assert self.j4.run.call_count == 0 # never called as it requires too many procs.
        assert "job-1" in q.running_or_done_queue.queue.keys()
        assert "job-2" in q.running_or_done_queue.queue.keys()
        assert "job-3" in q.running_or_done_queue.queue.keys()
        del q

    def test_list_jobs(self):
        q = mdrunr.Mdrunr(np_tot=2)
        q.add_job(self.j1)
        q.add_job(self.j2)
        q.add_job(self.j3)
        q.add_job(self.j4)
        job_list = q.list_jobs()
        try:
            assert self.j1 in job_list
            assert self.j2 in job_list
            assert self.j3 in job_list
            assert self.j4 in job_list
        except AssertionError:
            print job_list
        del q



if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestMdjob)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestMdrunr)
    alltests = unittest.TestSuite((suite1,suite2))
    unittest.TextTestRunner(verbosity=2).run(alltests)

