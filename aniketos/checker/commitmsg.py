import sys
import re

class ReferenceChecker(object):

    def __init__(self, keywords=('see', 'fixes', 'closes', 'refs'), whitelist=()):
        self._keywords = keywords
        self._whitelist = whitelist
        self._pattern = re.compile(r"(%s) \#(\d+)" % "|".join(self._keywords))

    def __call__(self, ref, commits):
        violations = []
        for commit in commits:
            summary = commit.summary

            if not summary.lower() in self._whitelist:
                if not self._pattern.search(summary.lower()):
                    violations.append(
                        (commit.hexsha, summary)
                    )
        sys.stdout.write(self._format(violations))
        return False if violations else True

    def _format(self, violations):
        output = []
        if violations:
            output.append("The following commits don't have suitable summary lines:")
            for rev, title in violations:
                output.append("  %s %s" % (rev, title))
        return "\n".join(output)

class NoRamblingChecker(object):

    def __init__(self, max_title_width=120):
        self._max_title_width = int(max_title_width)

    def _format(self, violations):
        output = []
        if violations:
            output.append("The following commits have long summaries.")
            output.append("Please keep the commit message summary line less than %d chars:" % self._max_title_width)
            for rev, title in violations:
                output.append("  %s %s" % (rev, title))

        return "\n".join(output)

    def __call__(self, ref, commits):
        violations = []
        for commit in commits:
            summary = commit.summary
            if len(summary) > self._max_title_width:
                violations.append(
                    (commit.hexsha, summary)
                )

        sys.stdout.write(self._format(violations))
        return False if violations else True
