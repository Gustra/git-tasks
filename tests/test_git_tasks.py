import yaml
from git import Repo
import os
import shutil
from subprocess import check_output, STDOUT
from tempfile import mkdtemp, NamedTemporaryFile
from unittest import TestCase
import unittest


class TestGittasks(TestCase):
    """
    Unit tests for git-tasks
    """
    program = os.path.join(os.path.dirname(__file__),
                           '..', 'bin', 'git-tasks')
    config_file = __file__.replace('.py', '.yml')

    def run_program(self, args, env=os.environ):
        return check_output([self.program] + list(args),
                            env=env, stderr=STDOUT)

    def setUp(self):
        self.gitdir = mkdtemp()
        os.chdir(self.gitdir)
        check_output(['git', 'init'])
        self.repo = Repo(self.gitdir)
        if 'GIT_TASKS_CONFIG_FILE' in os.environ:
            del os.environ['GIT_TASKS_CONFIG_FILE']

    def tearDown(self):
        shutil.rmtree(self.gitdir)

    def test_get_help(self):
        output = check_output([self.program, '--help'])
        self.assertIn('usage:', output)

    def test_create(self):
        """Test creating and switching branches"""
        output = self.run_program(['list'])
        self.assertEqual(output, '')
        t1 = 'issue-1'
        t2 = 'issue-2'

        # Create first task
        output = self.run_program(['start', t1])
        self.assertIn('Creating', output)
        self.assertIn(t1, output)
        self.assertIn(t1, self.repo.git.status())
        self.repo.git.commit('--allow-empty', '-m', 'Initial')
        self.assertIn(t1, self.repo.git.branch())

        # Create second task
        output = self.run_program(['start', t2])
        self.assertIn('Creating', output)
        self.assertIn(t2, self.repo.git.status())

        # Switch to first task
        output = self.run_program(['start', t1])
        self.assertIn('Switching', output)
        self.assertIn(t1, self.repo.git.status(), )

        output = self.run_program(['--config-file', self.config_file, 'list'])
        self.assertEqual(output, "{}\n{}\n".format(t1, t2))

    def test_status(self):
        """Test status command"""
        config_data = yaml.load('''
systems:
  - name: Generic
    type: generic
    our:
      command: fake-task-manager
    patterns:
      - generic-\d+
''')
        with NamedTemporaryFile() as config_fp:
            config_fp.write(yaml.dump(config_data))
            config_fp.flush()

            env = os.environ.copy()
            env['GIT_TASKS_CONFIG_FILE'] = config_fp.name

            output = self.run_program(['status'], env)
            self.assertIn('No tasks started', output)

            t1 = 'generic-1'
            output = self.run_program(['start', t1], env)
            self.assertIn('Installing', output)
            self.repo.git.commit('--allow-empty', '-m', 'Initial')
            self.assertIn(t1, self.repo.git.branch())

            output = self.run_program(['status'], env)
            self.assertEqual(output, 'generic-1 (): \n')

            env['FAKE_TITLE'] = 'First issue'
            env['FAKE_TASK'] = yaml.dump({'id': '1',
                                          'title': 'First issue',
                                          'status': 'New'})

            output = self.run_program(['status'], env)
            self.assertEqual(output, 'generic-1 (New): First issue\n')


if __name__ == '__main__':
    unittest.main()
