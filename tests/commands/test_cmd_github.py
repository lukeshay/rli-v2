from rli.commands import cmd_github
from rli.config import GithubConfig
from unittest.mock import patch, Mock
from unittest import TestCase
from rli import cli
from tests.helper import make_test_context
from rli.constants import ExitStatus
from rli import github

class CmdGithubTest(TestCase):
    def setUp(self):
        self.repo_name = "some name"
        self.repo_desc = "some description"
        self.repo_private = "true"

        self.github_config = GithubConfig({
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password"
        })

        self.mock_rli_config = Mock()
        self.mock_rli_config.github_config = self.github_config

        self.mock_github = Mock()

        self.mock_logging_info = Mock()

        github.Github = self.mock_github
        cmd_github.get_config_or_exit = self.mock_rli_config
        cmd_github.logging.info = self.mock_logging_info

    @patch("rli.github.RLIGithub.create_repo")
    @patch("sys.exit")
    def test_create_repo_success(self, mock_sys_exit, mock_create_repo):
        mock_create_repo.return_value = {"name": "some name"}

        with make_test_context(["github", "create-repo", "--repo-name", self.repo_name, "--repo-description", self.repo_desc, "--private", self.repo_private]) as ctx:
            cli.rli.invoke(ctx)

            self.mock_rli_config.assert_called_once()
            self.mock_logging_info.assert_called_with(f'Here is your new repo:\n{str({"name": "some name"})}')
            mock_sys_exit.assert_called_with(ExitStatus.OK)
            mock_create_repo.assert_called_with(self.repo_name, self.repo_desc, "true")

    @patch("rli.github.RLIGithub.create_repo")
    @patch("sys.exit")
    def test_create_repo_failure(self, mock_sys_exit, mock_create_repo):
        mock_create_repo.return_value = None
        with make_test_context(["github", "create-repo", "--repo-name", self.repo_name, "--repo-description", self.repo_desc, "--private", self.repo_private]) as ctx:
            cli.rli.invoke(ctx)

            self.mock_rli_config.assert_called_once()
            self.mock_logging_info.assert_not_called()
            mock_sys_exit.assert_called_with(ExitStatus.GITHUB_EXCEPTION_RAISED)
            mock_create_repo.assert_called_with(self.repo_name, self.repo_desc, "true")