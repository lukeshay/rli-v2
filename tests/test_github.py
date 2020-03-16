import unittest
import os
import subprocess
from rli.github import RLIGithub
from rli.config import GithubConfig
from unittest.mock import Mock, patch
from github import GithubException


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.valid_github_config = GithubConfig(
            {
                "organization": "some_org",
                "login": "some_login",
                "password": "some_password",
            }
        )

        self.create_repo_args = ("some name", "some description", "true")
        self.mock_create_repo = Mock()
        self.mock_get_user = Mock()

        self.mock_get_user.create_repo = self.mock_create_repo

        self.rli_github = RLIGithub(self.valid_github_config)

    @patch("github.Github.get_user")
    def test_valid_creation(self, mock_get_user):
        mock_get_user.return_value = self.mock_get_user

        self.rli_github.create_repo(*self.create_repo_args)

        mock_get_user.assert_called_once()
        self.mock_create_repo.assert_called_with(
            self.create_repo_args[0],
            description=self.create_repo_args[1],
            private=True,
            auto_init=True,
        )

    @patch("logging.error")
    @patch("github.Github.get_user")
    def test_raises_name_taken_github_exception(
        self, mock_get_user, mock_logging_error
    ):
        mock_get_user.side_effect = GithubException(422, "Failure")

        self.rli_github.create_repo(*self.create_repo_args)

        mock_get_user.assert_called_once()
        mock_logging_error.assert_called_with("Repository name is taken.")

    @patch("logging.error")
    @patch("github.Github.get_user")
    def test_raises_other_github_exception(self, mock_get_user, mock_logging_error):
        mock_get_user.side_effect = GithubException(400, "Failure")

        self.rli_github.create_repo(*self.create_repo_args)

        mock_get_user.assert_called_once()
        mock_logging_error.assert_called_with(
            "There was an exception when creating your repository."
        )

    @patch("subprocess.run")
    def test_checkout(self, mock_subprocess_run):
        self.rli_github.checkout("asdfasdf")
        mock_subprocess_run.assert_called_with(
            args=["git", "checkout", "asdfasdf"],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
