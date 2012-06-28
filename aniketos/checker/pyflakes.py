from __future__ import absolute_import

from aniketos.policy import DefaultAcceptPolicy

class PyflakesChecker(object):

    name = 'PYFLAKES'

    def __init__(self, git, staging_dir, accept_policy):
        self.git = git
        self.staging_dir = staging_dir
        self.accept_policy = accept_policy

    def __call__(self, refname, oldrev, newrev):
        # TODO: invoke pyflakes, get the results
        pass
