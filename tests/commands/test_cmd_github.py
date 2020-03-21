from github import GithubException
from rli import cli
from rli import github
from rli.commands import cmd_github
from rli.constants import ExitCode
from rli.exceptions import InvalidRLIConfiguration
from tests.helper import make_test_context
from unittest import TestCase
from unittest.mock import patch, Mock


class CmdGithubTest(TestCase):
    def setUp(self):
        self.repo_name = "some name"
        self.repo_desc = "some description"
        self.repo_private = "true"
        self.secrets = ("SECRET_ONE", "SECRET_TWO")

        self.mock_rli_config = Mock()

        self.mock_github = Mock()

        self.mock_logging_info = Mock()
        self.mock_logging_error = Mock()

        github.Github = self.mock_github
        cmd_github.get_rli_config_or_exit = self.mock_rli_config
        cmd_github.logging.info = self.mock_logging_info
        cmd_github.logging.error = self.mock_logging_error

    @patch("rli.github.RLIGithub.create_repo")
    @patch("sys.exit")
    def test_create_repo_success(self, mock_sys_exit, mock_create_repo):
        mock_create_repo.return_value = {"name": "some name"}

        with make_test_context(
            [
                "github",
                "create-repo",
                "--repo-name",
                self.repo_name,
                "--repo-description",
                self.repo_desc,
                "--private",
                self.repo_private,
            ]
        ) as ctx:
            cli.cli.invoke(ctx)

            self.mock_rli_config.assert_called_once()
            self.mock_logging_info.assert_called_with(
                f'Here is your new repo:\n{str({"name": "some name"})}'
            )
            mock_sys_exit.assert_called_with(ExitCode.OK)
            mock_create_repo.assert_called_with(self.repo_name, self.repo_desc, "true")

    @patch("rli.github.RLIGithub.create_repo")
    @patch("sys.exit")
    def test_create_repo_failure(self, mock_sys_exit, mock_create_repo):
        mock_create_repo.return_value = None
        with make_test_context(
            [
                "github",
                "create-repo",
                "--repo-name",
                self.repo_name,
                "--repo-description",
                self.repo_desc,
                "--private",
                self.repo_private,
            ]
        ) as ctx:
            cli.cli.invoke(ctx)

            self.mock_rli_config.assert_called_once()
            self.mock_logging_info.assert_not_called()
            mock_sys_exit.assert_called_with(ExitCode.GITHUB_ERROR)
            mock_create_repo.assert_called_with(self.repo_name, self.repo_desc, "true")

    @patch("rli.github.RLIGithub.add_secrets")
    @patch("sys.exit")
    def test_add_secrets(self, mock_sys_exit, mock_add_secrets):
        mock_add_secrets.return_value = None
        with make_test_context(
            [
                "github",
                "add-secrets",
                "--repo-name",
                self.repo_name,
                "-s",
                self.secrets[0],
                "--secret",
                self.secrets[1],
            ]
        ) as ctx:
            cli.cli.invoke(ctx)

            self.mock_rli_config.assert_called_once()
            mock_add_secrets.assert_called_once_with(
                self.repo_name, self.secrets, self.mock_rli_config().rli_secrets
            )
            self.mock_logging_info.assert_called_once_with(
                "Successfully added all secrets to your repo."
            )
            mock_sys_exit.assert_called_once_with(ExitCode.OK)

    @patch("rli.github.RLIGithub.add_secrets")
    @patch("sys.exit")
    def test_add_secrets_no_repo(self, mock_sys_exit, mock_add_secrets):
        mock_add_secrets.return_value = None
        mock_sys_exit.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            with make_test_context(
                [
                    "github",
                    "add-secrets",
                    "-s",
                    self.secrets[0],
                    "--secret",
                    self.secrets[1],
                ]
            ) as ctx:
                cli.cli.invoke(ctx)

        self.mock_rli_config.assert_not_called()
        mock_add_secrets.assert_not_called()
        self.mock_logging_info.assert_not_called()
        mock_sys_exit.assert_called_once_with(ExitCode.MISSING_ARG)
        self.mock_logging_error.assert_called_once_with("You must provide a repo name!")

    @patch("rli.github.RLIGithub.add_secrets")
    @patch("sys.exit")
    def test_add_secrets_invalid_rli_configuration(
        self, mock_sys_exit, mock_add_secrets
    ):
        mock_add_secrets.side_effect = InvalidRLIConfiguration
        mock_sys_exit.side_effect = SystemExit

        with self.assertRaises(SystemExit):
            with make_test_context(
                [
                    "github",
                    "add-secrets",
                    "--repo-name",
                    self.repo_name,
                    "-s",
                    self.secrets[0],
                    "--secret",
                    self.secrets[1],
                ]
            ) as ctx:
                cli.cli.invoke(ctx)

        self.mock_rli_config.assert_called_once()
        mock_add_secrets.assert_called_once_with(
            self.repo_name, self.secrets, self.mock_rli_config().rli_secrets
        )
        self.mock_logging_info.assert_not_called()
        self.mock_logging_error.assert_called_once_with(
            "Your Github RLI configuration is incorrect."
        )
        mock_sys_exit.assert_called_once_with(ExitCode.INVALID_RLI_CONFIG)

    @patch("rli.github.RLIGithub.add_secrets")
    @patch("sys.exit")
    def test_add_secrets_github_exception(self, mock_sys_exit, mock_add_secrets):
        mock_add_secrets.side_effect = GithubException(400, None)
        mock_sys_exit.side_effect = SystemExit

        with self.assertRaises(SystemExit):
            with make_test_context(
                [
                    "github",
                    "add-secrets",
                    "--repo-name",
                    self.repo_name,
                    "-s",
                    self.secrets[0],
                    "--secret",
                    self.secrets[1],
                ]
            ) as ctx:
                cli.cli.invoke(ctx)

        self.mock_rli_config.assert_called_once()
        mock_add_secrets.assert_called_once_with(
            self.repo_name, self.secrets, self.mock_rli_config().rli_secrets
        )
        self.mock_logging_info.assert_not_called()
        self.mock_logging_error.assert_called_once_with(
            "There was an error while adding secrets."
        )
        mock_sys_exit.assert_called_once_with(ExitCode.GITHUB_ERROR)

    @patch("rli.github.RLIGithub.add_secrets")
    @patch("sys.exit")
    def test_add_secrets_unexpected_exception(self, mock_sys_exit, mock_add_secrets):
        mock_add_secrets.side_effect = Exception
        mock_sys_exit.side_effect = SystemExit

        with self.assertRaises(SystemExit):
            with make_test_context(
                [
                    "github",
                    "add-secrets",
                    "--repo-name",
                    self.repo_name,
                    "-s",
                    self.secrets[0],
                    "--secret",
                    self.secrets[1],
                ]
            ) as ctx:
                cli.cli.invoke(ctx)

        self.mock_rli_config.assert_called_once()
        mock_add_secrets.assert_called_once_with(
            self.repo_name, self.secrets, self.mock_rli_config().rli_secrets
        )
        self.mock_logging_info.assert_not_called()
        self.mock_logging_error.assert_called_once_with(
            "There was an unexpected error while adding secrets."
        )
        mock_sys_exit.assert_called_once_with(ExitCode.UNEXPECTED_ERROR)
