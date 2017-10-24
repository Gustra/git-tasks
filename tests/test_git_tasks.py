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

    def test_clean(self):
        """Test creating and switching branches"""
        env = os.environ.copy()
        env['GIT_TASKS_CONFIG_FILE'] = self.config_file

        output = self.run_program(['list'], env)
        self.assertEqual(output, '')
        t1 = 'issue-1'
        t2 = 'issue-2'

        self.repo.git.commit('--allow-empty', '-m', 'Initial')
        self.repo.git.branch('origin/master')

        # Create first task
        self.run_program(['start', t1], env)
        self.repo.git.commit('--allow-empty', '-m', 't1')

        # Create second task
        self.run_program(['start', t2], env)
        self.repo.git.commit('--allow-empty', '-m', 't2')

        branches = sorted([h.name for h in self.repo.heads])
        self.assertListEqual(branches, sorted(['master', 'origin/master',
                                               t1, t2]))

        self.repo.git.checkout('origin/master')

        # Run clean where all branches should be preserved
        output = self.run_program(['clean'], env)
        self.assertEqual('', output)

        branches = sorted([h.name for h in self.repo.heads])
        self.assertListEqual(branches, sorted(['master', 'origin/master',
                                               t1, t2]))

        # Move origin/master to t2
        self.repo.git.reset('--hard', t2)

        # Clean t2
        output = self.run_program(['clean'], env)
        self.assertIn(t2, output)

        branches = sorted([h.name for h in self.repo.heads])
        self.assertListEqual(branches, sorted(['master', 'origin/master',
                                               t1]))

        self.repo.git.checkout(t1)
        self.repo.git.rebase()

        self.repo.git.checkout('origin/master')

        # Move origin/master to t1
        self.repo.git.reset('--hard', t1)

        # Dry run t1
        output = self.run_program(['clean', '--dry-run'], env)
        self.assertIn(t1, output)
        branches = sorted([h.name for h in self.repo.heads])
        self.assertListEqual(branches, sorted(['master', 'origin/master',
                                               t1]))

        # Clean t1
        output = self.run_program(['clean'], env)
        self.assertIn(t1, output)

        branches = sorted([h.name for h in self.repo.heads])
        self.assertListEqual(branches, sorted(['master', 'origin/master']))


if __name__ == '__main__':
    unittest.main()
