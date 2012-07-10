from aniketos.checker.pylint import PylintChecker
from aniketos.checker.commitmsg import NoRamblingChecker

CHECKER_TYPES = {}
CHECKER_TYPES['python.pylint'] = PylintChecker
CHECKER_TYPES['commitmsg.norambling'] = NoRamblingChecker

def get_checker_type(name):
    return CHECKER_TYPES[name]

