"""This module defines various accept policies. An AcceptPolicy determines
whether the push should be accepted or rejected based on the result from the
checker.
"""
import os
import cPickle

DefaultAcceptPolicy = lambda *a : True

def StrictAcceptPolicy(result):
    """This is the strictest accept policy.

    If there are any violations at all in :param result:, the method returns
    `False`, which means 'reject'
    """
    return len(result) == 0

def _sum_violations(msgid_occurence_map):
    return reduce(
        lambda aggregate, (msgid, occurences) : \
            aggregate + len(occurences),
        msgid_occurence_map.iteritems(),
        0)

class PreviousRunBasedPolicy(object):
    """This policy is based on previous results.

    If there's no previous result file,
    the current result will be saved as the previous result, and the push will
    pass.
    If there is the previous result file, each key in the previous result will
    be compared with the current result, if the number of violations for each
    key in the previous result increases, the push will be rejected.
    """
    def __init__(self, result_filepath):
        self.result_filepath = result_filepath

    def _load_result(self):
        if os.path.exists(self.result_filepath):
            with open(self.result_filepath, 'r') as f:
                return cPickle.load(f)
        else:
            return None

    def _save_result(self, result):
        with open(self.result_filepath, 'w') as f:
            cPickle.dump(dict(result), f)

    def __call__(self, result):
        previous_result = self._load_result()
        if previous_result is None:
            self._save_result(result)
            return True
        else:
            previous_files = set(previous_result.keys())
            current_files = set(result.keys())
            # the files we need to check are the intersection b/w
            # previous_files and current_files
            files_to_check = previous_files & current_files

            files_with_more_violations = []
            for file_ in files_to_check:
                num_previous_violations = _sum_violations(previous_result[file_])
                num_current_violations = _sum_violations(result[file_])
                if num_current_violations > num_previous_violations:
                    files_with_more_violations.append(
                        (file_,
                            (num_previous_violations, num_current_violations),
                            result[file_])
                    )

            if files_with_more_violations:
                print "The push introduced more violations on the following files:"
                for file_, (num_previous_violations, num_current_violations), violations in files_with_more_violations:
                    print " "*2, file_, \
                        "previous: %d" % num_previous_violations, \
                        "current: %d" % num_current_violations
                    # TODO: make this a formatter
                    from violation import Violations
                    print str(Violations(violations))
                return False
            else:
                previous_result.update(result)
                self._save_result(previous_result)
                return True
