import sys
import os
import re
import ConfigParser
from os.path import join
from os.path import abspath
from aniketos.checker import get_checker_type
from aniketos.policy import get_policy_type

STAGING_DIR = '/tmp/staging'
RESULT_FILE = '/tmp/result.pickle'

# Server hook is always invoked from the repo's root directory
REPO_ROOT_DIR = os.getcwd()

class Rule(object):

    def __init__(self, refmatcher, checker):
        self._refmatcher = refmatcher
        self._checker = checker

    def __call__(self, refname, oldrev, newrev):
        if re.search(self._refmatcher, refname):
            return self._checker(refname, oldrev, newrev)
        else:
            return True

RULES = [
    Rule('refs/heads/master',
        get_checker_type('pylint')(
            STAGING_DIR,
            get_policy_type('decremental')(RESULT_FILE)
        )
    )
]

def build_policies(cp, sections):
    for section in sections:
        items = cp.items(section)
        name = items['name']

def build_checkers(cp, sections, policies):
    pass

def build_rules(cp, sections, rules):
    pass

def read_config(fp):
    cp = ConfigParser.ConfigParser()
    cp.readfp(fp)
    sections = cp.sections()

    # sort out policies, checkers and rules
    policy_sections = filter(lambda x:x.startswith('policy'), sections)
    checker_sections  = filter(lambda x:x.startswith('checker'), sections)
    rule_sections  = filter(lambda x:x.startswith('rule'), sections)

    policies = build_policies(cp, policy_sections)
    checkers = build_checkers(cp, checker_sections, policies)
    rules = build_rules(cp, rule_sections, rules)

    return []

def main():
    """Git update hook.

    :param refname: Name of the ref, e.g., refs/heads/master
    :param oldrev: The old object name stored in the ref
    :param newrev: The new object name to be stored in the ref
    """
    refname, oldrev, newrev = sys.argv[1:]

    with open(join(REPO_ROOT_DIR, 'aniketos.ini')) as fp:
        rules = read_config(fp)

    accepted = True
    for rule in rules:
        accepted = accepted and rule(refname, oldrev, newrev)
        # We still run all the checkers,
        # so the user will know which checks failed
        if accepted:
            sys.exit(0)
        else:
            sys.exit(1)
