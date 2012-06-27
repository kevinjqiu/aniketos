from __future__ import absolute_import

import shutil
import sys
import os
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

    def __init__(self, git, staging_dir, previous_result_file):
        self.git = git
        self.staging_dir = staging_dir
        self.previous_result_file = previous_result_file

    def _nuke_dir_if_necessary(self, dir_):
        if os.path.exists(dir_):
            shutil.rmtree(dir_)

    def _create_dir(self, dir_):
        os.makedirs(dir_)

    def __call__(self, refname, oldrev, newrev):
        files = self.git.changed_files(oldrev, newrev)
        tree = self.git.ls_tree(newrev)

        changed_file_details = \
            [(file_, _) for (file_, _) in tree.iteritems() if file_ in files]

        self._nuke_dir_if_necessary(self.staging_dir)
        self._create_dir(self.staging_dir)
        # for each changed files, check out a local copy
        for file_, details in changed_file_details:
            abs_path = os.path.join(self.staging_dir, file_)
            self._create_dir(os.path.dirname(abs_path))
            with open(abs_path, 'w') as f:
                f.write(self.git.get_blob(details['hash']))

        print changed_file_details

# vim: set fdm=marker foldlevel=1:
