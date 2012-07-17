import random
from hashlib import sha1
from mock import Mock
from mock import patch
from aniketos.checker.commitmsg import ReferenceChecker

def commit(summary, **kwargs):
    kwargs.update({'summary':summary})
    retval = Mock(**kwargs)
    if not hasattr(retval, 'hexsha'):
        retval.hexsha = sha1(str(random.random())).hexdigest()
    return retval

def test_reference_checker___good_messages():
    checker = ReferenceChecker()
    commits = [commit("Fix a bad problem. (Fixes #12345)"),
        commit("Fix a new problem. Closes #54321"),
        commit("Introduced a new problem. See #54321")]

    assert True == checker(Mock(), commits)

@patch('sys.stdout')
def test_reference_checker___some_bad_messages(mock_stdout):
    checker = ReferenceChecker()

    commits = [commit("Fix a bad problem."),
        commit("Fix a new problem. Closes #54321"),
        commit("Introduced a new problem.")]

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

    commits = [commit("Migrations"),
        commit("Fix a new problem. Closes #54321"),
        commit("Introduced a new problem.")]

    assert False == checker(Mock(), commits)
    mock_stdout.write.assert_called_with("""\
The following commits don't have suitable summary lines:
  %s %s""" % (commits[2].hexsha, commits[2].summary))

