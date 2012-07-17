import mock
from cStringIO import StringIO
from aniketos.cli.update import main
from test import RepoTestBase
from test import _

class TestUpdate(RepoTestBase):

    def test_null_sha_in_newrev_should_be_ignored(self):
        config = StringIO("""\
[rule:refs/heads/master]
refmatch=master
checker=master
[checker:master]
type=aniketos.checker.commitmsg.NoRamblingChecker""")

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
type=aniketos.checker.commitmsg.NoRamblingChecker""")

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
type=aniketos.checker.commitmsg.NoRamblingChecker""")

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
type=aniketos.checker.commitmsg.NoRamblingChecker
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

    @mock.patch('sys.stdout')
    def test_update_master_must_have_ticket_number(self, mock_output):
        import aniketos.cli.update
        aniketos.cli.update.REPO_ROOT_DIR = _('repo/sample.git')

        config = StringIO("""\
[rule:refs/heads/master]
refmatch=master
checker=master
[checker:master]
type=aniketos.checker.commitmsg.ReferenceChecker""")

        status = main(['refs/heads/master',
            "0dea60ee1b95d26e376ceb175a52fd3e3a8ac2fc",
            "174c1870771b3b21869c44f3463dbd788bf024e2"],
            config
            )

        mock_output.write.assert_called_with("""\
The following commits don't have suitable summary lines:
  517b2f5b0932d6c002b7d655f9e8a4a6fbd69688 Obviously a complicated issue that needs a long rambling summary line.
  8fc20aaf3c066b5fe1ff84b7eb2e7ef28175807d commit 2""")
        assert 1 == status
