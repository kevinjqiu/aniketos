import aniketos.git as git

class NoRamblingChecker(object):

    def __init__(self, max_title_width):
        self._max_title_width = int(max_title_width)

    def __call__(self, refname, oldrev, newrev):
        violations = []
        for rev in git.revisions_in(oldrev, newrev):
            message = git.get_commit_message(rev)
            title = message.splitlines()[0]

            if len(title) > self._max_title_width:
                violations.append(
                    (rev, title)
                )
        if violations:
            print "The following commits have long titles. Please keep the commit message subject line less than %d chars" % self._max_title_width
            for rev, title in violations:
                print "  ", rev, title

            return False
        else:
            return True
