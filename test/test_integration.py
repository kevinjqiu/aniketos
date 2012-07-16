import mock
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
refmatch=master
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
refmatch=master
checker=master
[checker:master]
type=message.norambling""")

        status = main(['refs/heads/master',
            '0'*40,
            '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33'],
            config
            )
        assert 0 == status

    def test_update_master_two_commits(self):
        import aniketos.cli.update
        aniketos.cli.update.REPO_ROOT_DIR = _('repo/sample.git')

        config = StringIO("""\
[rule:refs/heads/master]
refmatch=master
checker=master
[checker:master]
type=message.norambling""")

        status = main(['refs/heads/master',
            "0dea60ee1b95d26e376ceb175a52fd3e3a8ac2fc",
            "8fc20aaf3c066b5fe1ff84b7eb2e7ef28175807d"],
            config
            )

        assert 0 == status

    @mock.patch('sys.stdout')
    def test_update_master_rambling_on_summary(self, mock_output):
        import aniketos.cli.update
        aniketos.cli.update.REPO_ROOT_DIR = _('repo/sample.git')

        config = StringIO("""\
[rule:refs/heads/master]
refmatch=master
checker=master
[checker:master]
type=message.norambling
max_title_width=20""")

        status = main(['refs/heads/master',
            "0dea60ee1b95d26e376ceb175a52fd3e3a8ac2fc",
            "517b2f5b0932d6c002b7d655f9e8a4a6fbd69688"],
            config
            )

        mock_output.write.assert_called_with("""\
The following commits have long summaries.
Please keep the commit message summary line less than 20 chars:
  517b2f5b0932d6c002b7d655f9e8a4a6fbd69688 Obviously a complicated issue that needs a long rambling summary line.""")
        assert 1 == status