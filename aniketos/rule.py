import re

class Rule(object):

    def __init__(self, refmatch, checkers):
        self._refmatch = refmatch
        self._checkers = checkers

    def __call__(self, ref, commits):
        if re.search(self._refmatch, ref.name):
            retval = True
            for checker in self._checkers.values():
                retval = retval and checker(ref, commits)
            return retval
        else:
            return True

    def get_checker(self, checker_name):
        return self._checkers[checker_name]
