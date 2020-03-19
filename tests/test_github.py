import unittest
from rli.github import RLIGithub, GITHUB_URL
from rli import github
from rli.config import GithubConfig
from unittest.mock import Mock, patch
from github import GithubException
from tests.helper import MockResponse


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.repo_name = "some-name"
        self.public_key = "1PjwOt4yg9yZsEQLUOCPqZRigVMPA4g+6cuGc2ssS1c="
        self.public_key_id = "09835109"

        self.secret_name = "A_SECRET"
        self.secret_value = "AKDJFLS"

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

        self.mock_response_return = {
            "key": self.public_key,
            "key_id": self.public_key_id,
        }

        self.mock_requests_get = Mock()
        self.mock_requests_get.return_value = MockResponse(
            200, self.mock_response_return
        )

        github.requests.get = self.mock_requests_get

        self.mock_requests_put = Mock()
        self.mock_requests_put.return_value = MockResponse(
            204, self.mock_response_return
        )

        github.requests.put = self.mock_requests_put

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

    def test_encrypt_secret(self):
        encrypted = self.rli_github._encrypt_secret(
            "1PjwOt4yg9yZsEQLUOCPqZRigVMPA4g+6cuGc2ssS1c=", "SOME_SECRET_VALUE"
        )

        self.assertIsNotNone(encrypted)

    def test_get_public_key_success(self):
        resp_json = self.rli_github.get_public_key(self.repo_name)
        self.assertEqual(self.mock_response_return, resp_json)
        self.mock_requests_get.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.valid_github_config.organization}/{self.repo_name}/actions/secrets/public-key",
            auth=(self.valid_github_config.login, self.valid_github_config.password),
        )

    def test_get_public_key_unsuccessful(self):
        self.mock_requests_get.return_value = MockResponse(403, self.mock_requests_get)

        with self.assertRaises(GithubException) as context:
            self.rli_github.get_public_key(self.repo_name)

        self.assertEqual(403, context.exception.status)
        self.assertEqual(self.mock_requests_get, context.exception.data)
        self.mock_requests_get.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.valid_github_config.organization}/{self.repo_name}/actions/secrets/public-key",
            auth=(self.valid_github_config.login, self.valid_github_config.password),
        )

    def test__put_encrypted_secret(self):
        self.rli_github._put_encrypted_secret(
            self.repo_name, self.public_key_id, self.secret_name, self.secret_value
        )

        self.mock_requests_put.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.valid_github_config.organization}/{self.repo_name}/actions/secrets/{self.secret_name}",
            auth=(self.valid_github_config.login, self.valid_github_config.password),
            json={"encrypted_value": self.secret_value, "key_id": self.public_key_id},
        )

    def test_add_secrets_no_secrets(self):
        self.rli_github.add_secrets(
            self.repo_name, [], {self.secret_name: self.secret_value}
        )

        self.mock_requests_get.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.valid_github_config.organization}/{self.repo_name}/actions/secrets/public-key",
            auth=(self.valid_github_config.login, self.valid_github_config.password),
        )

        self.mock_requests_put.assert_called_once()

    def test_add_secrets_some_secrets(self):
        self.rli_github.add_secrets(
            self.repo_name, [self.secret_name], {self.secret_name: self.secret_value}
        )

        self.mock_requests_get.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.valid_github_config.organization}/{self.repo_name}/actions/secrets/public-key",
            auth=(self.valid_github_config.login, self.valid_github_config.password),
        )

        self.mock_requests_put.assert_called_once()

    def test_add_secrets_error_request(self):
        self.mock_requests_put.return_value = MockResponse(
            400, self.mock_response_return
        )

        with self.assertRaises(GithubException) as context:
            self.rli_github.add_secrets(
                self.repo_name,
                [self.secret_name],
                {self.secret_name: self.secret_value},
            )

        self.mock_requests_get.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.valid_github_config.organization}/{self.repo_name}/actions/secrets/public-key",
            auth=(self.valid_github_config.login, self.valid_github_config.password),
        )
        self.mock_requests_put.assert_called_once()
        self.assertEqual(400, context.exception.status)
