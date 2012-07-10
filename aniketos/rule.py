import re

class Rule(object):

    def __init__(self, refmatch, checker):
        self._refmatch = refmatch
        self._checker = checker

    def __call__(self, refname, oldrev, newrev):
        if re.search(self._refmatch, refname):
            return self._checker(refname, oldrev, newrev)
        else:
            return True

