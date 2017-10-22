from os import getenv

import yaml
from git import Repo
import os
import shutil
from subprocess import check_output, STDOUT
from tempfile import mkdtemp, NamedTemporaryFile
from unittest import TestCase
import unittest


class TestPrepareCommitMsg(TestCase):
    """
    Unit tests for prepare-commit-msg
    """
    here = os.path.join(os.path.dirname(__file__))
    root = os.path.join(os.path.dirname(__file__), '..')
    bin_path = os.path.join(root, 'bin')
    program = os.path.join(root, 'hooks', 'prepare-commit-msg')
    task_manager = os.path.join(here, 'helpers', 'fake-task-manager')
    os.environ['PATH'] = '{}/helpers:{}:{}'.format(here,
                                                   bin_path,
                                                   getenv('PATH'), )
    gitdir = None
    repo = None

    def run_program(self, args, env=os.environ):
        return check_output([self.program] + args,
                            env=env, stderr=STDOUT)

    @classmethod
    def create_commit(cls, message):
        cls.repo.git.commit('--allow-empty', '-m', message)

    @classmethod
    def setUpClass(cls):
        cls.gitdir = mkdtemp()
        cls.hook = os.path.join(cls.gitdir, '.git', 'hooks',
                                'prepare-commit-msg')
        os.chdir(cls.gitdir)
        check_output(['git', 'init'])
        cls.repo = Repo(cls.gitdir)
        cls.create_commit('Initial')
        cls.repo.git.branch('issue-2')

        # Make sure our environment is not tainted
        if 'FAKE_TITLE' in os.environ:
            del (os.environ['FAKE_TITLE'])

    @classmethod
    def tearDownClass(cls):
        if cls.gitdir:
            shutil.rmtree(cls.gitdir)

    def test_prepare_message(self):
        """Test hook prepare-commit-msg"""
        t1 = 'generic-1'

        config_data = yaml.load('''
systems:
  - name: Generic
    type: generic
    our:
      command: {}
    patterns: [ "generic-([0-9]+)" ]
    message-format: generic #
            '''.format(self.task_manager))
        with NamedTemporaryFile() as config_fp:
            config_fp.write(yaml.dump(config_data))
            config_fp.flush()

            env = os.environ.copy()
            env['GIT_TASKS_CONFIG_FILE'] = config_fp.name

            with NamedTemporaryFile() as msg_fp:
                #
                # not on a task branch
                #
                msg_fp.write('Just a commit message\n')
                msg_fp.flush()
                output = self.run_program([msg_fp.name, ','], env)
                self.assertEqual(output, '')
                msg_fp.seek(0)
                output = msg_fp.read()
                self.assertEqual(output, 'Just a commit message\n')

                #
                # Start task generic-1
                #

                self.assertFalse(os.path.exists(self.hook))
                output = check_output(['git-tasks', 'start', t1], env=env)
                self.assertIn('Installing', output)
                self.assertTrue(os.path.exists(self.hook))

                #
                # Task without title
                #
                msg_fp.seek(0)
                msg_fp.truncate()
                msg_fp.write('Just a commit message\n')
                msg_fp.flush()
                output = self.run_program([msg_fp.name], env)
                self.assertEqual(output, '')
                msg_fp.seek(0)
                output = msg_fp.read()
                self.assertEqual(output,
                                 '\n\ngeneric-1\n\n'
                                 'Just a commit message\n')

                #
                # Task with title
                #
                env['FAKE_TITLE'] = 'First issue'
                env['FAKE_TASK'] = yaml.dump({'id': '1',
                                              'title': 'First issue'})
                msg_fp.seek(0)
                msg_fp.truncate()
                msg_fp.write('Just a commit message\n')
                msg_fp.flush()
                output = self.run_program([msg_fp.name], env)
                self.assertEqual(output, '')
                msg_fp.seek(0)
                output = msg_fp.read()
                self.assertEqual(output,
                                 '\n\ngeneric #1 First issue\n\n'
                                 'Just a commit message\n')

                #
                # Don't update existing row in message
                #
                env['FAKE_TITLE'] = 'First issue'
                env['FAKE_TASK'] = yaml.dump({'id': '1',
                                              'title': 'First issue'})
                output = self.run_program([msg_fp.name], env)
                self.assertEqual(output, '')
                msg_fp.seek(0)
                output = msg_fp.read()
                self.assertEqual(output,
                                 '\n\ngeneric #1 First issue\n\n'
                                 'Just a commit message\n')


if __name__ == '__main__':
    unittest.main()
