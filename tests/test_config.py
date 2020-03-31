from unittest import mock
from rli.config import (
    DockerConfig,
    GithubConfig,
    DockerDeployConfig,
    DeployConfig,
    get_deploy_config_or_exit,
)
from rli.exceptions import InvalidRLIConfiguration, InvalidDeployConfiguration
from rli.constants import ExitCode
from unittest.mock import patch
from unittest import TestCase


class DockerConfigTest(TestCase):
    def setUp(self):
        self.valid_config = {
            "registry": "some_repo",
            "login": "some_login",
            "password": "some_password",
        }

        self.valid_config_diff = {
            "registry": "some_rep",
            "login": "some_login",
            "password": "some_password",
        }

        self.no_login_config = {"registry": "some_repo", "password": "some_password"}

        self.no_password_config = {"registry": "some_repo", "login": "some_login"}

        self.no_registry_config = {"login": "some_login", "password": "some_password"}

        self.github_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password",
        }

    @patch("rli.config.load_config")
    def test_valid_config(self, mock_load_config):
        mock_load_config.return_value = {"docker": self.valid_config}
        docker_config = DockerConfig()

        self.assertEqual(self.valid_config["registry"], docker_config.registry)
        self.assertEqual(self.valid_config["login"], docker_config.login)
        self.assertEqual(self.valid_config["password"], docker_config.password)

    @patch("rli.config.load_config")
    def test_no_registry_config(self, mock_load_config):
        mock_load_config.return_value = {"docker": self.no_registry_config}
        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Docker registry was not provided. ",
            str(context.exception),
        )

    @patch("rli.config.load_config")
    def test_no_password_config(self, mock_load_config):
        mock_load_config.return_value = {"docker": self.no_password_config}

        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Docker password was not provided.",
            str(context.exception),
        )

    @patch("rli.config.load_config")
    def test_no_login_config(self, mock_load_config):
        mock_load_config.return_value = {"docker": self.no_login_config}

        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig()

        # Don't forget the space at the end
        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Docker login was not provided. ",
            str(context.exception),
        )

    @patch("rli.config.load_config")
    def test_eq(self, mock_load_config):
        mock_load_config.return_value = {"docker": self.valid_config}
        docker_config_one = DockerConfig()
        mock_load_config.return_value = {"docker": self.valid_config}
        docker_config_two = DockerConfig()

        self.assertEqual(docker_config_one, docker_config_two)

        mock_load_config.return_value = {"docker": self.valid_config_diff}
        docker_config_two = DockerConfig()

        self.assertNotEqual(docker_config_one, docker_config_two)

        mock_load_config.return_value = {"github": self.github_config}
        docker_config_two = GithubConfig()

        self.assertNotEqual(docker_config_one, docker_config_two)


class GithubConfigTest(TestCase):
    def setUp(self):
        self.valid_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password",
        }

        self.no_login_config = {"organization": "some_org", "password": "some_password"}

        self.no_password_config = {"organization": "some_org", "login": "some_login"}

        self.no_organization_config = {
            "username": "some_name",
            "login": "some_login",
            "password": "some_password",
        }

        self.no_org_or_username_config = {
            "login": "some_login",
            "password": "some_password",
        }

        self.docker_config = {
            "registry": "some_repo",
            "login": "some_login",
            "password": "some_password",
        }

    @patch("rli.config.load_config")
    def test_valid_config(self, mock_load_config):
        mock_load_config.return_value = {"github": self.valid_config}
        github_config = GithubConfig()

        self.assertEqual(self.valid_config["organization"], github_config.organization)
        self.assertEqual(self.valid_config["login"], github_config.login)
        self.assertEqual(self.valid_config["password"], github_config.password)

    @patch("rli.config.load_config")
    def test_no_password_config(self, mock_load_config):
        mock_load_config.return_value = {"github": self.no_password_config}
        github_config = GithubConfig()

        self.assertEqual(
            self.no_password_config["organization"], github_config.organization
        )
        self.assertEqual(self.no_password_config["login"], github_config.login)
        self.assertEqual("", github_config.password)

    @patch("rli.config.load_config")
    def test_username_config(self, mock_load_config):
        mock_load_config.return_value = {"github": self.no_organization_config}
        github_config = GithubConfig()

        self.assertEqual(
            self.no_organization_config["username"], github_config.username
        )
        self.assertEqual(self.no_organization_config["login"], github_config.login)
        self.assertEqual(
            self.no_organization_config["password"], github_config.password
        )

    @patch("rli.config.load_config")
    def test_no_org_or_username_config(self, mock_load_config):
        mock_load_config.return_value = {"github": self.no_org_or_username_config}
        with self.assertRaises(InvalidRLIConfiguration) as context:
            GithubConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Github organization or username was not provided. ",
            str(context.exception),
        )

    @patch("rli.config.load_config")
    def test_no_login_config(self, mock_load_config):
        mock_load_config.return_value = {"github": self.no_login_config}
        with self.assertRaises(InvalidRLIConfiguration) as context:
            GithubConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Github login was not provided.",
            str(context.exception),
        )

    @patch("rli.config.load_config")
    def test_eq(self, mock_load_config):
        mock_load_config.return_value = {"github": self.valid_config}
        github_config_one = GithubConfig()
        github_config_two = GithubConfig()

        self.assertEqual(github_config_one, github_config_two)

        mock_load_config.return_value = {"github": self.no_password_config}
        github_config_two = GithubConfig()

        self.assertNotEqual(github_config_one, github_config_two)

        mock_load_config.return_value = {"docker": self.docker_config}
        github_config_two = DockerConfig()

        self.assertNotEqual(github_config_one, github_config_two)


class DockerDeployConfigTest(TestCase):
    def setUp(self):
        self.valid_config = {
            "image": "this is an image",
            "compose_file": "deploy/compose.yml",
        }

        self.valid_config_no_compose = {"image": "this is another image"}

        self.invalid_config = {"compose_file": "deploy/compose.yml"}

        self.github_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password",
        }

    def test_valid_config(self):
        docker_deploy_config = DockerDeployConfig(self.valid_config)

        self.assertEqual(
            self.valid_config["compose_file"], docker_deploy_config.compose_file
        )
        self.assertEqual(self.valid_config["image"], docker_deploy_config.image)

    def test_valid_config_no_compose(self):
        docker_deploy_config = DockerDeployConfig(self.valid_config_no_compose)

        self.assertIsNone(docker_deploy_config.compose_file)
        self.assertEqual(
            self.valid_config_no_compose["image"], docker_deploy_config.image
        )

    def test_invalid_config(self):
        with self.assertRaises(InvalidDeployConfiguration) as context:
            DockerDeployConfig(self.invalid_config)

        self.assertEqual(
            "InvalidDeployConfiguration has been raised: No docker image specified. ",
            str(context.exception),
        )

    @patch("rli.config.load_config")
    def test_eq(self, mock_load_config):
        mock_load_config.return_value = {"github": self.github_config}

        docker_deploy_config_one = DockerDeployConfig(self.valid_config)
        docker_deploy_config_two = DockerDeployConfig(self.valid_config)

        self.assertEqual(docker_deploy_config_one, docker_deploy_config_two)

        docker_deploy_config_two = DockerDeployConfig(self.valid_config_no_compose)

        self.assertNotEqual(docker_deploy_config_one, docker_deploy_config_two)

        github_config = GithubConfig()

        self.assertNotEqual(docker_deploy_config_one, github_config)


class DeployConfigTest(TestCase):
    def setUp(self):
        self.valid_config = {
            "secrets": ["THIS_IS_SECRET"],
            "docker": {
                "image": "this is an image",
                "compose_file": "deploy/compose.yml",
            },
        }

        self.valid_config_no_secrets = {
            "docker": {
                "image": "this is an image",
                "compose_file": "deploy/compose.yml",
            }
        }

        self.invalid_config = {"secrets": ["THIS_IS_SECRET"]}

        self.github_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password",
        }

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_valid_config(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        deploy_config = DeployConfig()

        docker_deploy_config = DockerDeployConfig(self.valid_config["docker"])

        self.assertEqual(docker_deploy_config, deploy_config.docker_deploy_config)
        self.assertEqual(self.valid_config["secrets"], deploy_config.secrets)

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_valid_config_no_secrets(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config_no_secrets
        mock_open.read_data = str(self.valid_config_no_secrets)

        deploy_config = DeployConfig()

        docker_deploy_config = DockerDeployConfig(
            self.valid_config_no_secrets["docker"]
        )

        self.assertEqual(docker_deploy_config, deploy_config.docker_deploy_config)
        self.assertEqual([], deploy_config.secrets)

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_valid_config_no_secrets(self, mock_open, mock_load):
        mock_load.return_value = self.invalid_config
        mock_open.read_data = str(self.invalid_config)

        with self.assertRaises(InvalidDeployConfiguration) as context:
            DeployConfig()

        self.assertEqual(
            "InvalidDeployConfiguration has been raised: No configuration specified.",
            str(context.exception),
        )

    @patch("rli.config.load_config")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_eq(self, mock_open, mock_load, mock_load_config):
        mock_load_config.return_value = {"github": self.github_config}

        mock_load.return_value = self.valid_config_no_secrets
        mock_open.read_data = str(self.valid_config_no_secrets)

        deploy_config_one = DeployConfig()
        deploy_config_two = DeployConfig()

        self.assertEqual(deploy_config_one, deploy_config_two)

        github_config = GithubConfig()

        self.assertNotEqual(deploy_config_one, github_config)

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_get_config_or_exit_valid_config(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        deploy_config = get_deploy_config_or_exit()
        docker_config = DockerDeployConfig(self.valid_config["docker"])

        self.assertEqual(docker_config, deploy_config.docker_deploy_config)

    @patch("sys.exit")
    @patch("builtins.open")
    @patch("logging.exception")
    def test_get_deploy_config_or_exit_no_file(
        self, mock_logging_exception, mock_open, mock_exit
    ):
        mock_open.side_effect = FileNotFoundError
        get_deploy_config_or_exit()

        self.assertEqual(ExitCode.NO_DEPLOY_JSON, mock_exit.call_args[0][0])
        self.assertTrue(
            "Could not find config/config.json", mock_logging_exception.call_args[0][0]
        )

    @patch("sys.exit")
    @patch("builtins.open")
    @patch("logging.exception")
    def test_get_deploy_config_or_exit_invalid_configuration(
        self, mock_logging_exception, mock_open, mock_exit
    ):
        mock_open.side_effect = InvalidDeployConfiguration
        get_deploy_config_or_exit()

        self.assertEqual(ExitCode.INVALID_DEPLOY_CONFIG, mock_exit.call_args[0][0])
        self.assertTrue(
            "Your config/config.json file is invalid.",
            mock_logging_exception.call_args[0][0],
        )
