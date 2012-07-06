from aniketos.checker.pylint import PylintChecker

CHECKER_TYPES = {}
CHECKER_TYPES['pylint'] = PylintChecker

def get_checker_type(name):
    return CHECKER_TYPES[name]

