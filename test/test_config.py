from cStringIO import StringIO
from aniketos.cli.config_parser import AniketosConfigParser
from aniketos.checker import PylintChecker
from aniketos.policy import Decremental

class TestConfigParser(object):
    def setup(self):
        self.cp = AniketosConfigParser()

    def test_read_config___no_rules(self):
        fp = StringIO("")
        assert len(self.cp.readfp(fp)) == 0

    def test_read_config___simple_rule(self):
        fp = StringIO("""[rule:foo]
refmatch=refs/heads/mybranch
checker=foochecker
[checker:foochecker]
type=pylint
staging_dir=/tmp
policy=foopolicy
[policy:foopolicy]
type=decremental
result_filepath=/tmp/staging
""")
        rules = self.cp.readfp(fp)
        assert len(rules) == 1
        assert isinstance(rules['foo'].get_checker('foo'), PylintChecker)

    def test_read_config___simple_rule_with_multiple_checkers(self):
        fp = StringIO("""[rule:foo]
refmatch=refs/heads/mybranch
checker=foochecker, barchecker
[checker:foochecker]
type=pylint
staging_dir=/tmp/foo
policy=foopolicy
[policy:foopolicy]
type=decremental
result_filepath=/tmp/foo/staging
[checker:barchecker]
type=pylint
staging_dir=/tmp/bar
policy=barpolicy
[policy:barpolicy]
type=decremental
result_filepath=/tmp/bar/staging
""")
        rules = self.cp.readfp(fp)

        assert len(rules) == 1

        assert isinstance(rules['foo'].get_checker('foo'), PylintChecker)
        assert rules['foo'].get_checker('foo').staging_dir, '/tmp/foo'
        assert isinstance(rules['foo'].get_checker('foo').policy, Decremental)

        assert isinstance(rules['foo'].get_checker('bar'), PylintChecker)
        assert rules['foo'].get_checker('bar').staging_dir, '/tmp/bar'
        assert isinstance(rules['foo'].get_checker('bar').policy, Decremental)

