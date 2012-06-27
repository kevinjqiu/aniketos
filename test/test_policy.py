from aniketos.policy import StrictAcceptPolicy
from nose.tools import eq_

def test_strict_policy():
    eq_(True, StrictAcceptPolicy({}))

def test_strict_policy():
    violations = {
        'foo.py' : { "W100" : [ (1, '') ] }
        }
    eq_(False, StrictAcceptPolicy(violations))
