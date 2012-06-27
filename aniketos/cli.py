import git
import sys
from os.path import join
from os.path import abspath
from aniketos.checker.pylint import PylintChecker
from aniketos.policy import StrictAcceptPolicy

STAGING_DIR = '/tmp/staging'
PREVIOUS_RESULT_FILE = '/tmp/previous.db'

CHECKERS = {
    'refs/heads/master' : [PylintChecker(git, STAGING_DIR, accept_policy=StrictAcceptPolicy)]
}

def update(refname, oldrev, newrev):
    """Git update hook.

    Signature:
        :param refname: Name of the ref, e.g., refs/heads/master
        :param oldrev: The old object name stored in the ref
        :param newrev: The new object name to be stored in the ref
    """

    if refname in CHECKERS:
        checkers = CHECKERS[refname]
        for checker in checkers:
            checker(refname, oldrev, newrev)
    else:
        # No checker found for refname
        # skipping...
        sys.exit(0)

    # TODO: correct exit status
    sys.exit(1)

def main():
    update(*sys.argv[1:])
