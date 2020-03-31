from unittest import TestCase
from unittest.mock import Mock
from rli import git
from rli.git import RLIGit


class RLIGitTest(TestCase):
    def setUp(self):
        self.commit = "THIS IS A COMMIT"
        self.mock_bash_run_command = Mock()
        self.mock_bash_run_command.returncode = 0
        self.mock_logging_debug = Mock()

        git.bash.run_command = self.mock_bash_run_command
        git.logging.debug = self.mock_logging_debug

    def test_checkout(self):
        RLIGit.checkout(self.commit)

        self.mock_logging_debug.assert_called_once_with(f"Checking out: {self.commit}")
        self.mock_bash_run_command.assert_called_once_with(
            ["git", "checkout", self.commit]
        )
