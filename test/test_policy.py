from aniketos.policy import get_policy_type
from nose.tools import eq_

Strict = get_policy_type('strict')

def test_strict_policy():
    eq_(True, Strict()({}))

def test_strict_policy():
    violations = {
        'foo.py' : { "W100" : [ (1, '') ] }
        }
    eq_(False, Strict()(violations))
