import sys
from os.path import join
from os.path import abspath
from aniketos import git
from aniketos.checker.pylint import PylintChecker
from aniketos.policy import StrictAcceptPolicy
from aniketos.policy import PreviousRunBasedPolicy

STAGING_DIR = '/tmp/staging'
RESULT_FILE = '/tmp/result.pickle'

CHECKERS = {
    'refs/heads/master' : [PylintChecker(git, STAGING_DIR,
        PreviousRunBasedPolicy(RESULT_FILE))]
}

def main():
    """Git update hook.

    :param refname: Name of the ref, e.g., refs/heads/master
    :param oldrev: The old object name stored in the ref
    :param newrev: The new object name to be stored in the ref
    """
    refname, oldrev, newrev = sys.argv[1:]

    if refname in CHECKERS:
        checkers = CHECKERS[refname]
        accepted = True
        for checker in checkers:
            accepted = accepted and checker(refname, oldrev, newrev)

        # We still run all the checkers,
        # so the user will know which checks failed
        if accepted:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # No checker found for refname
        # skipping...
        sys.exit(0)