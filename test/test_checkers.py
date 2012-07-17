import random
from hashlib import sha1
from mock import Mock
from mock import patch
from aniketos.checker.commitmsg import ReferenceChecker
from aniketos.checker.commitmsg import NoRamblingChecker
from aniketos.checker.python import get_affected_files_from_commits
from test import RepoTestBase

def mk_commit(summary, **kwargs):
    kwargs.update({'summary':summary})
    retval = Mock(**kwargs)
    if not 'hexsha' in kwargs:
        retval.hexsha = sha1(str(random.random())).hexdigest()
    return retval

def test_reference_checker___good_messages():
    checker = ReferenceChecker()
    commits = [mk_commit("Fix a bad problem. (Fixes #12345)"),
        mk_commit("Fix a new problem. Closes #54321"),
        mk_commit("Introduced a new problem. See #54321")]

    assert True == checker(Mock(), commits)

@patch('sys.stdout')
def test_reference_checker___some_bad_messages(mock_stdout):
    checker = ReferenceChecker()

    commits = [mk_commit("Fix a bad problem."),
        mk_commit("Fix a new problem. Closes #54321"),
        mk_commit("Introduced a new problem.")]

    assert False == checker(Mock(), commits)
    mock_stdout.write.assert_called_with("""\
The following commits don't have suitable summary lines:
  %s %s
  %s %s""" % (
      commits[0].hexsha, commits[0].summary,
      commits[2].hexsha, commits[2].summary))

@patch('sys.stdout')
def test_reference_checker___with_whitelist(mock_stdout):
    checker = ReferenceChecker(whitelist=['migrations'])

    commits = [mk_commit("Migrations"),
        mk_commit("Fix a new problem. Closes #54321"),
        mk_commit("Introduced a new problem.")]

    assert False == checker(Mock(), commits)
    mock_stdout.write.assert_called_with("""\
The following commits don't have suitable summary lines:
  %s %s""" % (commits[2].hexsha, commits[2].summary))

@patch('sys.stdout')
def test_no_rambling___rambling(mock_stdout):
    checker = NoRamblingChecker(max_title_width=20)

    commits = [mk_commit('a'*19),
        mk_commit('b'*20),
        mk_commit('c'*21),
        mk_commit('d'*99)]

    assert False == checker(Mock(), commits)
    mock_stdout.write.assert_called_with("""\
The following commits have long summaries.
Please keep the commit message summary line less than 20 chars:
  %s %s
  %s %s""" % (commits[2].hexsha, commits[2].summary,
      commits[3].hexsha, commits[3].summary))

class TestAffectedFiles(RepoTestBase):

    def test___files_modified(self):
        commits = self.repo.iter_commits("174c1870771b3b21869c44f3463dbd788bf024e2..4afe0b36b7772865115aba82d1bc8942e2c3e9d6")
        affected_files = get_affected_files_from_commits(commits)
        assert 1 == len(affected_files['modified'])
        assert 0 == len(affected_files['added'])
        assert 0 == len(affected_files['deleted'])
        assert affected_files['modified'][0] == 'highlighty.py'
