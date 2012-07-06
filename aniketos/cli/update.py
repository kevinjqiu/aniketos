import sys
import os
import re
from os.path import join
from os.path import abspath
from aniketos.checker import PylintChecker
from aniketos.policy import StrictAcceptPolicy
from aniketos.policy import PreviousRunBasedPolicy

STAGING_DIR = '/tmp/staging'
RESULT_FILE = '/tmp/result.pickle'

# Server hook is always invoked from the repo's root directory
REPO_ROOT_DIR = os.getcwd()

class Rule(object):

    def __init__(self, refmatcher, checker):
        self._refmatcher = refmatcher
        self._checker = checker

    def __call__(self, refname, oldrev, newrev):
        if re.search(self._refmatcher, refname):
            return self._checker(refname, oldrev, newrev)
        else:
            return True

RULES = [
    Rule('refs/heads/master',
        PylintChecker(STAGING_DIR,
            PreviousRunBasedPolicy(RESULT_FILE))
    )
]

def main():
    """Git update hook.

    :param refname: Name of the ref, e.g., refs/heads/master
    :param oldrev: The old object name stored in the ref
    :param newrev: The new object name to be stored in the ref
    """
    refname, oldrev, newrev = sys.argv[1:]

    accepted = True
    for rule in RULES:
        accepted = accepted and rule(refname, oldrev, newrev)
        # We still run all the checkers,
        # so the user will know which checks failed
        if accepted:
            sys.exit(0)
        else:
            sys.exit(1)
