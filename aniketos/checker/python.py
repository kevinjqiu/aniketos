from __future__ import absolute_import

import shutil
import sys
import os
import json
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

def get_affected_blobs_from_commits(commits):
    """Get a list of changed files from the commit range."""
    commit_list = list(commits)
    if len(commit_list) == 0:
        return []
    else:
        parent = commit_list[-1].iter_parents().next()
        diffs = parent.diff(commit_list[0])

        retval = {'modified':set([]),
            'deleted':set([]),
            'added':set([])
            }

        for diff in diffs:
            if diff.new_file:
                retval['added'].add(diff.b_blob)
            elif diff.deleted_file:
                retval['deleted'].add(diff.a_blob)
            else:
                assert diff.a_blob.path == diff.b_blob.path
                retval['modified'].add(diff.a_blob)

        return retval

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

    def _checkout_blobs(self, blobs):
        for blob in blobs:
            abs_path = os.path.join(self.staging_dir, blob.path)
            self._create_dir_if_necessary(os.path.dirname(abs_path))
            with open(abs_path, 'w') as f:
                blob.stream_data(f)

    def __call__(self, ref, commits):
        files_affected = get_affected_blobs_from_commits(commits)

        self._nuke_dir_if_necessary(self.staging_dir)
        self._create_dir_if_necessary(self.staging_dir)

        self._checkout_blobs(files_affected['added'])
        self._checkout_blobs(files_affected['modified'])

        # run pylint on added and modified files
        # TODO: remember to use abs path

        # result = self._run_pylint(abs_paths)
        # return self.policy(result)
        return None

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
