import sys

class NoRamblingChecker(object):

    def __init__(self, max_title_width=120):
        self._max_title_width = int(max_title_width)

    def __call__(self, ref, commits):
        violations = []
        for commit in commits:
            summary = commit.summary
            if len(summary) > self._max_title_width:
                violations.append(
                    (commit.hexsha, summary)
                )

        output = []
        if violations:
            output.append("The following commits have long summaries.")
            output.append("Please keep the commit message summary line less than %d chars:" % self._max_title_width)
            for rev, title in violations:
                output.append("  %s %s" % (rev, title))

            sys.stdout.write("\n".join(output))
            return False
        else:
            return True
