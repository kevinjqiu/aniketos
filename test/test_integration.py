from cStringIO import StringIO
from os.path import abspath
from os.path import join
from os.path import dirname
from git import Repo
from shutil import copytree
from shutil import rmtree
from aniketos.cli.update import main

TEST_ROOT = dirname(abspath(__file__))

def _(relpath):
    return join(TEST_ROOT, relpath)

class TestUpdate(object):

    def load_repo(self):
        try:
            rmtree(_('repo/sample.git'))
        except:
            pass
        copytree(_('fixtures/sample.git'), _('repo/sample.git'))
        return Repo(_('repo/sample.git'))

    def setup(self):
        self.repo = self.load_repo()

    def test_null_sha_in_newrev_should_be_ignored(self):
        config = StringIO("""\
[rule:refs/heads/master]
refmatch=refs/heads/master
checker=master
[checker:master]
type=message.norambling""")

        status = main(['refs/heads/master',
            '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33',
            '0'*40],
            config
            )
        assert 0 == status

    def test_null_sha_in_oldrev_should_be_ignored(self):
        config = StringIO("""\
[rule:refs/heads/master]
refmatch=refs/heads/master
checker=master
[checker:master]
type=message.norambling""")

        status = main(['refs/heads/master',
            '0'*40,
            '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33'],
            config
            )
        assert 0 == status

