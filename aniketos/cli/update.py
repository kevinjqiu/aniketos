import sys
import os
import re
import ConfigParser
from os.path import join
from os.path import abspath
from aniketos.checker import get_checker_type
from aniketos.policy import get_policy_type

# Server hook is always invoked from the repo's root directory
REPO_ROOT_DIR = os.getcwd()

class Rule(object):

    def __init__(self, refmatch, checker):
        self._refmatch = refmatch
        self._checker = checker

    def __call__(self, refname, oldrev, newrev):
        if re.search(self._refmatch, refname):
            return self._checker(refname, oldrev, newrev)
        else:
            return True

def build_policies(cp, sections):
    retval = {}
    for section in sections:
        items = dict(cp.items(section))
        _, name = section.split(':')
        type_ = items.pop('type')
        retval[name] = get_policy_type(type_)(**items)
    return retval

def build_checkers(cp, sections, policies):
    retval = {}
    for section in sections:
        items = dict(cp.items(section))
        _, name = section.split(':')
        type_ = items.pop('type')
        items['policy'] = policies[items['policy']]
        retval[name] = get_checker_type(type_)(**items)
    return retval

def build_rules(cp, sections, checkers):
    retval = {}
    for section in sections:
        items = dict(cp.items(section))
        _, name = section.split(':')
        items['checker'] = checkers[items['checker']]
        retval[name] = Rule(**items)
    return retval

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
    rules = build_rules(cp, rule_sections, checkers)

    return rules

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
    for rule in rules.values():
        accepted = accepted and rule(refname, oldrev, newrev)
        # We still run all the checkers,
        # so the user will know which checks failed
        if accepted:
            sys.exit(0)
        else:
            sys.exit(1)
