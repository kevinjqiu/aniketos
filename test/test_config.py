from cStringIO import StringIO
from aniketos.cli.update import read_config

def test_read_config___no_rules():
    fp = StringIO("")
    assert [] == read_config(fp)

def test_read_config___simple_rule():
    fp = StringIO("""[rule:foo]
        """)
    rules = read_config(fp)
    assert len(rules) == 1
