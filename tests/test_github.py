from github import GithubException
from rli import github
from rli.constants import ExitCode
from rli.github import RLIGithub, GITHUB_URL
from tests.helper import MockGithubConfig, MockResponse
from unittest import TestCase
from unittest.mock import Mock, patch


class RLIGithubTest(TestCase):
    def setUp(self):
        self.repo_name = "some-repo-name"
        self.organization = "some_org"
        self.login = "some_login"
        self.public_key = {
            "key": "1PjwOt4yg9yZsEQLUOCPqZRigVMPA4g+6cuGc2ssS1c=",
            "key_id": "THIS_IS_THE_ID",
        }

        self.secrets_to_add = ("SECRET_ONE", "SECRET_TWO")
        self.secrets = {
            "SECRET_ONE": "secret-one",
            "SECRET_TWO": "secret-two",
            "SECRET_THREE": "secret-three",
        }

        self.mock_logging_debug = Mock()
        self.mock_logging_error = Mock()

        self.mock_github_config = MockGithubConfig(
            self.organization, None, self.login, ""
        )
        self.mock_get_config_or_exit = Mock()
        self.mock_get_config_or_exit.return_value = self.mock_github_config

        self.mock_repo = Mock()

        self.mock_create_repo = Mock()
        self.mock_create_repo.return_value = self.mock_repo

        self.mock_github = Mock()
        self.mock_github.return_value.get_user.return_value.create_repo = (
            self.mock_create_repo
        )

        self.mock_exit = Mock()

        self.mock_get_response = MockResponse(200, self.public_key)
        self.mock_get = Mock()
        self.mock_get.return_value = self.mock_get_response

        self.mock_put_response = MockResponse(200, self.public_key)
        self.mock_put = Mock()
        self.mock_put.return_value = self.mock_get_response

        github.Github = self.mock_github
        github.logging.debug = self.mock_logging_debug
        github.logging.error = self.mock_logging_error
        github.sys.exit = self.mock_exit
        github.requests.get = self.mock_get
        github.requests.put = self.mock_put
        github.get_github_config_or_exit = self.mock_get_config_or_exit

        self.rli_github = RLIGithub()
        # self.rli_github._config = self.mock_github_config

    def test_successful_create_repo_private(self):
        repo = self.rli_github.create_repo(self.repo_name, private="true")

        self.assertEqual(self.mock_repo, repo)
        self.mock_logging_debug.assert_called_once_with(
            f"Creating repo '{self.repo_name}'."
        )
        self.mock_logging_error.assert_not_called()
        self.mock_create_repo.assert_called_once_with(
            self.repo_name, description="", private=True, auto_init=True
        )
        self.mock_exit.assert_not_called()

    def test_successful_create_repo_public(self):
        repo = self.rli_github.create_repo(
            self.repo_name, repo_description="YOOTY", private="false"
        )

        self.assertEqual(self.mock_repo, repo)
        self.mock_logging_debug.assert_called_once_with(
            f"Creating repo '{self.repo_name}'."
        )
        self.mock_logging_error.assert_not_called()
        self.mock_create_repo.assert_called_once_with(
            self.repo_name, description="YOOTY", private=False, auto_init=True
        )
        self.mock_exit.assert_not_called()

    def test_create_repo_raises_GithubException_name_taken(self):
        self.mock_create_repo.side_effect = GithubException(422, None)
        repo = self.rli_github.create_repo(
            self.repo_name, repo_description="YOOTY", private="false"
        )

        self.assertEqual(None, repo)
        self.mock_logging_debug.assert_called_once_with(
            f"Creating repo '{self.repo_name}'."
        )
        self.mock_create_repo.assert_called_once_with(
            self.repo_name, description="YOOTY", private=False, auto_init=True
        )
        self.mock_logging_error.assert_called_once_with("Repository name is taken.")
        self.mock_exit.assert_called_once_with(ExitCode.GITHUB_ERROR)

    def test_create_repo_raises_GithubException_unknown(self):
        self.mock_create_repo.side_effect = GithubException(400, None)
        repo = self.rli_github.create_repo(
            self.repo_name, repo_description="YOOTY", private="false"
        )

        self.assertEqual(None, repo)
        self.mock_logging_debug.assert_called_once_with(
            f"Creating repo '{self.repo_name}'."
        )
        self.mock_create_repo.assert_called_once_with(
            self.repo_name, description="YOOTY", private=False, auto_init=True
        )
        self.mock_logging_error.assert_called_once_with(
            "There was an exception when creating your repository."
        )
        self.mock_exit.assert_called_once_with(ExitCode.GITHUB_ERROR)

    def test_successful_get_public_key(self):
        public_key = self.rli_github.get_public_key(self.repo_name)

        self.assertEqual(self.mock_get_response.json(), public_key)
        self.mock_get.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.mock_github_config.organization}/{self.repo_name}/actions/secrets/public-key",
            auth=(self.mock_github_config.login, self.mock_github_config.password),
        )

    def test_not_ok_get_public_key(self):
        self.mock_get_response = MockResponse(400, None)
        self.mock_get.return_value = self.mock_get_response
        self.rli_github.get_public_key(self.repo_name)

        self.mock_get.assert_called_once_with(
            url=f"{GITHUB_URL}/repos/{self.mock_github_config.organization}/{self.repo_name}/actions/secrets/public-key",
            auth=(self.mock_github_config.login, self.mock_github_config.password),
        )

        self.mock_logging_error.assert_called_once_with("Could not get public key.")
        self.mock_exit.assert_called_once_with(ExitCode.GITHUB_ERROR)

    def test_add_secrets(self):
        self.rli_github.add_secrets(self.repo_name, self.secrets_to_add, self.secrets)

        self.mock_put.assert_called()
        self.mock_logging_debug.assert_called_once_with(
            f"Adding secrets to repo '{self.repo_name}'."
        )

    @patch("rli.github.RLIGithub._put_encrypted_secret")
    def test_add_secrets_bad_response(self, mock_put_secret):
        mock_put_secret.return_value = MockResponse(300, None)

        with self.assertRaises(GithubException):
            self.rli_github.add_secrets(
                self.repo_name, self.secrets_to_add, self.secrets
            )

        mock_put_secret.assert_called_once()
        self.mock_logging_debug.assert_called_once_with(
            f"Adding secrets to repo '{self.repo_name}'."
        )

    def test_add_secrets_no_secrets(self):
        self.rli_github.add_secrets(self.repo_name, None, self.secrets)

        self.mock_put.assert_called()
        self.mock_logging_debug.assert_called_once_with(
            f"Adding secrets to repo '{self.repo_name}'."
        )

    def test_github_twice(self):
        github = self.rli_github.github
        self.assertEqual(github, self.rli_github.github)
        self.mock_github.assert_called_once_with(self.login)
