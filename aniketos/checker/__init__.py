from aniketos.checker.pylint import PylintChecker

CHECKER_TYPES = {}

def get_checker_type(name):
    return CHECKER_TYPES[name]

CHECKER_TYPES['pylint'] = PylintChecker
