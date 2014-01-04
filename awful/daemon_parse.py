"""
awftools
========

Sub-parsers for the commands that can be sent to awfqd.
"""

from argparse import ArgumentParser

cmd_parse = {
  "sub"  : ArgumentParser(description="Submit a job"      ),
  "del"  : ArgumentParser(description="Delete a job"      ),
}

cmd_parse['sub'].add_argument('cmd', help='Commandline string')
cmd_parse['sub'].add_argument('--name', help='Unique name for this job', default=None)
cmd_parse['sub'].add_argument('-n', '--nproc', help='Number of processors required', type=int, default=1)
cmd_parse['sub'].add_argument('-m', '--mpi', help='Run in mpi mode', action='store_true', default=False)
cmd_parse['sub'].add_argument('-d', '--dir', help='Set working directory', default=None)
cmd_parse['sub'].add_argument('-c', '--combine', help='Redirects stderr to stdout', action='store_true', default=False)

cmd_parse['del'].add_argument('name', help='Name of job you want to delete')
 
