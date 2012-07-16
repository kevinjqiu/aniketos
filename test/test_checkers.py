from mock import Mock
from mock import patch
from aniketos.checker.commitmsg import ReferenceChecker

def test_reference_checker___good_messages():
    checker = ReferenceChecker()
    ref = Mock()
    commits = [Mock(), Mock(), Mock()]

    commits[0].hexsha = "517b2f5b0932d6c002b7d655f9e8a4a6fbd69688"
    commits[0].summary = "Fix a bad problem. (Fixes #12345)"

    commits[1].hexsha = "8fc20aaf3c066b5fe1ff84b7eb2e7ef28175807d5"
    commits[1].summary = "Fix a new problem. Closes #54321"

    commits[2].hexsha = "517b2f5b0932d6c002b7d655f9e8a4a6fbd696888"
    commits[2].summary = "Introduced a new problem. See #54321"

    assert True == checker(ref, commits)

@patch('sys.stdout')
def test_reference_checker___some_bad_messages(mock_stdout):
    checker = ReferenceChecker()

    ref = Mock()
    commits = [Mock(), Mock(), Mock()]

    commits[0].hexsha = "517b2f5b0932d6c002b7d655f9e8a4a6fbd69688"
    commits[0].summary = "Fix a bad problem"

    commits[1].hexsha = "8fc20aaf3c066b5fe1ff84b7eb2e7ef28175807d5"
    commits[1].summary = "Fix a new problem. Closes #54321"

    commits[2].hexsha = "517b2f5b0932d6c002b7d655f9e8a4a6fbd696888"
    commits[2].summary = "Introduced a new problem"

    assert False == checker(ref, commits)
    mock_stdout.write.assert_called_with("""\
The following commits don't have suitable summary lines:
  517b2f5b0932d6c002b7d655f9e8a4a6fbd69688 Fix a bad problem
  517b2f5b0932d6c002b7d655f9e8a4a6fbd696888 Introduced a new problem""")
