from os.path import abspath
from os.path import join
from os.path import dirname
from shutil import copytree
from shutil import rmtree
from git import Repo

TEST_ROOT = dirname(abspath(__file__))

def _(relpath):
    return join(TEST_ROOT, relpath)

class RepoTestBase(object):

    def setup(self):
        self.repo = self.load_repo()

    def load_repo(self):
        try:
            rmtree(_('repo/sample.git'))
        except:
            pass
        copytree(_('fixtures/sample.git'), _('repo/sample.git'))
        return Repo(_('repo/sample.git'))
