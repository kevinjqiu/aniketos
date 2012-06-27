import commands
import re
from functools import partial

def ls_tree(rev):
    """Get the tree given the revision hash.
    """
    output = commands.getoutput('git ls-tree -r ' + rev)
    objects = output.splitlines()

    retval = {}
    for (mode, type_, hash_, rel_path) in map(partial(re.split, r'\s+'), objects):
        retval[rel_path] = {
            'mode' : mode,
            'type' : type_,
            'hash' : hash_
        }
    return retval

def changed_files(oldrev, newrev):
    """Get the files changed from newrev to oldrev.
    """
    output = commands.getoutput('git diff --name-only %s %s' % (oldrev, newrev))
    return output.splitlines()
