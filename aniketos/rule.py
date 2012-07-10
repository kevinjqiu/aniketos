import re

class Rule(object):

    def __init__(self, refmatch, checkers):
        self._refmatch = refmatch
        self._checkers = checkers

    def __call__(self, refname, oldrev, newrev):
        if re.search(self._refmatch, refname):
            retval = True
            for checker in self._checkers.values():
                retval = retval and checker(refname, oldrev, newrev)
            return retval
        else:
            return True

    def get_checker(self, checker_name):
        return self._checkers[checker_name]
