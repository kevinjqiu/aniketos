import git
import sys
from sys import exit

WATCHED_REF = 'refs/heads/master'

def update(refname, oldrev, newrev):
    """Git update hook.

    Signature:
        :param refname: Name of the ref, e.g., refs/heads/master
        :param oldrev: The old object name stored in the ref
        :param newrev: The new object name to be stored in the ref
    """

    if refname == WATCHED_REF:
        files = git.changed_files(oldrev, newrev)
        tree = git.ls_tree(newrev)

        changed_file_details = \
                [(file_, _) for (file_, _) in tree.iteritems() if file_ in files]
        print changed_file_details


    # TODO: correct exit status
    exit(1)

def main():
    update(*sys.argv[1:])
