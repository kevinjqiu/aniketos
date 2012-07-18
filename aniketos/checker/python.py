from __future__ import absolute_import

import shutil
import sys
import os
import json
from aniketos import git
from collections import defaultdict
from pylint.reporters import BaseReporter
from pylint.interfaces import IReporter
from pylint.lint import Run

# Pylint checker {{{2
# Reporter {{{ 3
class MessageCollector(BaseReporter):

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
        # We're only collecting messages
        pass
# }}}

def get_affected_files_from_commits(commits):
    """Get a list of changed files from the commit range."""
    commit_list = list(commits)
    if len(commit_list) == 0:
        return []
    else:
        parent = commit_list[-1].iter_parents().next()
        diffs = parent.diff(commit_list[0])

        changed_files = set([])
        deleted_files = set([])
        added_files = set([])

        for diff in diffs:
            if diff.new_file:
                added_files.add(diff.b_blob.path)
            elif diff.deleted_file:
                deleted_files.add(diff.a_blob.path)
            else:
                assert diff.a_blob.path == diff.b_blob.path
                changed_files.add(diff.a_blob.path)

        return dict(modified=list(changed_files),
            deleted=list(deleted_files),
            added=list(added_files))

class PylintChecker(object):

    def __init__(self, staging_dir, policy, rcfile=None):
        self.staging_dir = staging_dir
        self.rcfile = rcfile
        self.policy = policy

    def _nuke_dir_if_necessary(self, dir_):
        if os.path.exists(dir_):
            shutil.rmtree(dir_)

    def _create_dir_if_necessary(self, dir_):
        if not os.path.exists(dir_):
            os.makedirs(dir_)

    def __call__(self, refname, oldrev, newrev):
        """Run Pylint on candidate files, return a list of violations.

            :param refname: refname
            :param oldrev: old revision hash
            :param newrev: new revision hash
            :return: list of violations from files touched between oldrev...newrev
        """
        files = git.changed_files(oldrev, newrev)
        tree = git.ls_tree(newrev)

        changed_file_details = \
            [(file_, _) for (file_, _) in tree.iteritems() if file_ in files]

        self._nuke_dir_if_necessary(self.staging_dir)
        self._create_dir_if_necessary(self.staging_dir)

        # for each changed files, check out a local copy
        abs_paths = []
        for file_, details in changed_file_details:
            abs_path = os.path.join(self.staging_dir, file_)
            self._create_dir_if_necessary(os.path.dirname(abs_path))
            with open(abs_path, 'w') as f:
                f.write(git.get_blob(details['hash']))
            abs_paths.append(abs_path)

        result = self._run_pylint(abs_paths)
        return self.policy(result)

    def _run_pylint(self, abs_paths):
        reporter = MessageCollector(self.staging_dir)

        if self.rcfile:
            args = ['--rcfile=%s' % self.rcfile]
        else:
            args = []
        args.extend(list(abs_paths))

        if args:
            Run(args,
                reporter=reporter,
                exit=False)

            return reporter.messages
        else:
            return {}
# }}}

# vim: set fdm=marker foldlevel=1:
