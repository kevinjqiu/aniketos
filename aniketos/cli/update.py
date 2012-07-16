import sys
import os
from git import Repo
from os.path import join
from aniketos.cli.config_parser import AniketosConfigParser

# Server hook is always invoked from the repo's root directory
REPO_ROOT_DIR = os.getcwd()
NULL_REV = '0'*40

def get_reference(refname):
    refname = refname.split('/')[-1]
    repo = Repo(REPO_ROOT_DIR)
    ref = filter(lambda ref : ref.name == refname, repo.refs)
    for ref in repo.refs:
        if ref.name == refname:
            return ref
    return None

def run(ref, commits, rules):
    accepted = True
    for rule in rules.values():
        accepted = accepted and rule(ref, commits)
        # We still run all the checkers,
        # so the user will know which checks failed
    return 0 if accepted else 1

def main(argv=None, config=None):
    """Git update hook.

    :param refname: Name of the ref, e.g., refs/heads/master
    :param oldrev: The old object name stored in the ref
    :param newrev: The new object name to be stored in the ref
    """
    if argv is None:
        argv = sys.argv[1:]

    refname, oldrev, newrev = argv

    if NULL_REV in (newrev, oldrev):
        # the branch is created or deleted,
        # we don't need to check them in these cases.
        return 0

    if config is None:
        config = open(join(REPO_ROOT_DIR, 'aniketos.ini'))

    configparser = AniketosConfigParser()
    rules = configparser.readfp(config)
    config.close()

    ref = get_reference(refname)

    if ref is None:
        raise "'%s' not found." % (refname,)

    commits = ref.repo.iter_commits('%s..%s' % (oldrev, newrev))
    return run(ref, commits, rules)
