from __future__ import absolute_import

import shutil
import sys
import os
import json
from collections import defaultdict
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

    def __init__(self, git, staging_dir, previous_result_file, rcfile=None):
        self.git = git
        self.staging_dir = staging_dir
        self.previous_result_file = previous_result_file
        self.rcfile = rcfile

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

        abs_paths = []
        for file_, details in changed_file_details:
            abs_path = os.path.join(self.staging_dir, file_)
            self._create_dir(os.path.dirname(abs_path))
            with open(abs_path, 'w') as f:
                f.write(self.git.get_blob(details['hash']))
            abs_paths.append(abs_path)

        result = self._run_pylint(abs_paths)
        print result

    def _run_pylint(self, abs_paths):
        # TODO: a better idiom for 'throwing away output'?
        import cStringIO
        output = cStringIO.StringIO()
        reporter = JsonReporter(self.staging_dir, output=output)
        del output

        if self.rcfile:
            args = ['--rcfile %s' % self.rcfile]
        else:
            args = []
        args.extend(list(abs_paths))

        Run(args,
            reporter=reporter,
            exit=False)

        return reporter.messages

# vim: set fdm=marker foldlevel=1:
