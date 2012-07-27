import random
from hashlib import sha1
from mock import Mock
from mock import patch
from aniketos.checker.commitmsg import ReferenceChecker
from aniketos.checker.commitmsg import NoRamblingChecker
from aniketos.checker.python import get_affected_blobs_from_commits
from aniketos.checker.python import PylintChecker
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

def MockPylintChecker(staging_dir, mock_policy):
    checker = PylintChecker(staging_dir, mock_policy, None)
    checker._nuke_dir_if_necessary = Mock()
    checker._create_dir_if_necessary = Mock()
    checker._checkout_blobs = Mock()
    checker._run_pylint = Mock()
    return checker

def MockPolicy(retval):
    policy = Mock()
    policy.return_value = retval
    return policy

class TestAffectedFiles(RepoTestBase):

    def test___no_commit(self):
        commits = self.repo.iter_commits("174c1870771b3b21869c44f3463dbd788bf024e2..174c1870771b3b21869c44f3463dbd788bf024e2")
        affected_files = get_affected_blobs_from_commits(commits)
        assert len(affected_files) == 0

    def test___files_modified(self):
        commits = self.repo.iter_commits("174c1870771b3b21869c44f3463dbd788bf024e2..4afe0b36b7772865115aba82d1bc8942e2c3e9d6")
        affected_files = get_affected_blobs_from_commits(commits)
        assert 1 == len(affected_files['modified'])
        assert 0 == len(affected_files['added'])
        assert 0 == len(affected_files['deleted'])
        assert [x.path for x in affected_files['modified']] == ['highlighty.py']

    def test___file_added(self):
        commits = self.repo.iter_commits("4afe0b36b7772865115aba82d1bc8942e2c3e9d6..e791bd14d48b0235fa8d3fd664190347eeccef0e")
        affected_files = get_affected_blobs_from_commits(commits)
        assert 1 == len(affected_files['added'])
        assert 0 == len(affected_files['modified'])
        assert 0 == len(affected_files['deleted'])
        assert [x.path for x in affected_files['added']] == ['new.py']

    def test___file_moved(self):
        commits = self.repo.iter_commits("e791bd14d48b0235fa8d3fd664190347eeccef0e..91f3a34167e775c166f00218ad126618ed655a74")
        affected_files = get_affected_blobs_from_commits(commits)
        assert 1 == len(affected_files['added'])
        assert 0 == len(affected_files['modified'])
        assert 1 == len(affected_files['deleted'])
        assert [x.path for x in affected_files['added']] == ['new_new.py']
        assert [x.path for x in affected_files['deleted']] == ['new.py']

    def test___file_deleted(self):
        commits = self.repo.iter_commits("91f3a34167e775c166f00218ad126618ed655a74..1af27ee144dc797ace07fa520211bc4cee75b6aa")
        affected_files = get_affected_blobs_from_commits(commits)
        assert 0 == len(affected_files['added'])
        assert 0 == len(affected_files['modified'])
        assert 1 == len(affected_files['deleted'])
        assert [x.path for x in affected_files['deleted']] == ['NEW_FILE_COMMIT2']

    def test___all_operations(self):
        commits = self.repo.iter_commits("8fc20aaf3c066b5fe1ff84b7eb2e7ef28175807d..1af27ee144dc797ace07fa520211bc4cee75b6aa")
        affected_files = get_affected_blobs_from_commits(commits)

        assert 2 == len(affected_files['added'])
        assert 0 == len(affected_files['modified'])
        assert 1 == len(affected_files['deleted'])
        assert [x.path for x in affected_files['deleted']] == ['NEW_FILE_COMMIT2']

    def test___right_files_are_collected(self):
        checker = MockPylintChecker('/var/staging/', MockPolicy(True))
        commits = self.repo.iter_commits("e791bd14d48b0235fa8d3fd664190347eeccef0e..91f3a34167e775c166f00218ad126618ed655a74")
        assert True == checker(None, commits)
        checker._run_pylint.assert_called_with(['/var/staging/new_new.py',])

    def test___exclude_non_python_files_to_run_with_pylint(self):
        checker = MockPylintChecker('/var/staging/', MockPolicy(True))
        commits = self.repo.iter_commits("e791bd14d48b0235fa8d3fd664190347eeccef0e..b2a12e4736312228fe9ce724d76dd16628d3e9aa")
        assert True == checker(None, commits)
        checker._run_pylint.assert_called_with(['/var/staging/new_new.py',])

        class Matcher(object):
            def __eq__(self, other):
                return set([blob.path for blob in other]) == \
                    set(['new_new.py', 'README.md'])

            def __ne__(self, other):
                return not self.__eq__(other)

        checker._checkout_blobs.assert_called_with(Matcher())
