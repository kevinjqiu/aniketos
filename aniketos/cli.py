import git
import sys
from aniketos.checker.pylint import PylintChecker
from sys import exit

CHECKERS = {
    'refs/heads/master' : [PylintChecker(git)]
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
    exit(1)

def main():
    update(*sys.argv[1:])
