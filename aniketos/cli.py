import git
import sys
from os.path import join
from os.path import abspath
from aniketos.checker.pylint import PylintChecker
from aniketos.policy import StrictAcceptPolicy

STAGING_DIR = '/tmp/staging'
RESULT_FILE = '/tmp/result.pickle'

CHECKERS = {
    'refs/heads/master' : [PylintChecker(git, STAGING_DIR,
        accept_policy=PreviousRunBasedPolicy(RESULT_FILE))]
}

def update(refname, oldrev, newrev):
    """Git update hook.

    :param refname: Name of the ref, e.g., refs/heads/master
    :param oldrev: The old object name stored in the ref
    :param newrev: The new object name to be stored in the ref
    """

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

    # TODO: correct exit status
    sys.exit(1)

def main():
    update(*sys.argv[1:])
