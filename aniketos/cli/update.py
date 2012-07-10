import sys
import os
from os.path import join
from os.path import abspath
from aniketos.cli.config_parser import AniketosConfigParser

# Server hook is always invoked from the repo's root directory
REPO_ROOT_DIR = os.getcwd()
ZERO_REV = '0'*40

def main():
    """Git update hook.

    :param refname: Name of the ref, e.g., refs/heads/master
    :param oldrev: The old object name stored in the ref
    :param newrev: The new object name to be stored in the ref
    """
    refname, oldrev, newrev = sys.argv[1:]

    if ZERO_REV in (newrev, oldrev):
        # the branch is created or deleted,
        # we don't need to check them in these cases.
        sys.exit(0)

    with open(join(REPO_ROOT_DIR, 'aniketos.ini')) as fp:
        configparser = AniketosConfigParser()
        rules = configparser.readfp(fp)

    accepted = True
    for rule in rules.values():
        accepted = accepted and rule(refname, oldrev, newrev)
        # We still run all the checkers,
        # so the user will know which checks failed
        if accepted:
            sys.exit(0)
        else:
            sys.exit(1)
