"""This module defines various accept policies. An AcceptPolicy determines
whether the push should be accepted or rejected based on the result from the
checker.
"""

def StrictAcceptPolicy(result):
    """This is the strictest accept policy.
    If there are any violations at all in :param result:,
    the method returns `False`
    """
    return len(result) == 0
