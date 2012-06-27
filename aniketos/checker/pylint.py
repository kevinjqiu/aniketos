from __future__ import absolute_import

import sys
from pylint.reporters import BaseReporter
from pylint.interfaces import IReporter
from pylint.lint import Run

# Reporter {{{ 2
class JsonReporter(BaseReporter):

    __implements__ = IReporter

    def __init__(self, root, output=sys.stdout):
        BaseReporter.__init__(self, output)
        # messages is in the following format:
        # filepath : { msgid : [ (lineno, msg) ] }
        self.root = root
        self.messages = defaultdict(lambda : defaultdict(list))

    def add_message(self, msg_id, location, msg):
        path, module, obj, line, col_offset = location

        relpath = path[len(self.root)+1:]
        self.messages[relpath][msg_id].append(
            (line, msg)
        )

    def display_results(self, layout):
        self.writeln(json.dumps(self.messages))
# }}}

class PylintChecker(object):

    def __init__(self, git):
        self.git = git

    def __call__(self, refname, oldrev, newrev):
        files = self.git.changed_files(oldrev, newrev)
        tree = self.git.ls_tree(newrev)

        changed_file_details = \
            [(file_, _) for (file_, _) in tree.iteritems() if file_ in files]

        print changed_file_details

# vim: set fdm=marker foldlevel=1:
