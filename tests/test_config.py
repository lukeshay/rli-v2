import io
import unittest
from unittest import mock
from rli.config import DockerConfig, GithubConfig, RLIConfig, get_config_or_exit
from rli.exceptions import InvalidRLIConfiguration
from rli.constants import ExitStatus


class DockerConfigTest(unittest.TestCase):
    def setUp(self):
        self.valid_config = {
            "registry": "some_repo",
            "login": "some_login",
            "password": "some_password"
        }

        self.no_login_config = {
            "registry": "some_repo",
            "password": "some_password"
        }

        self.no_password_config = {
            "registry": "some_repo",
            "login": "some_login"
        }

        self.no_registry_config = {
            "login": "some_login",
            "password": "some_password"
        }

        self.github_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password"
        }

    def test_valid_config(self):
        docker_config = DockerConfig(self.valid_config)

        self.assertEqual(self.valid_config["registry"], docker_config.registry)
        self.assertEqual(self.valid_config["login"], docker_config.login)
        self.assertEqual(self.valid_config["password"], docker_config.password)

    def test_no_registry_config(self):
        docker_config = DockerConfig(self.no_registry_config)

        self.assertEqual("", docker_config.registry)
        self.assertEqual(self.no_registry_config["login"], docker_config.login)
        self.assertEqual(self.no_registry_config["password"], docker_config.password)

    def test_no_password_config(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig(self.no_password_config)

        self.assertEqual("InvalidRLIConfiguration has been raised: Docker password was not provided.",
                         str(context.exception))

    def test_no_login_config(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig(self.no_login_config)

        # Don't forget the space at the end
        self.assertEqual("InvalidRLIConfiguration has been raised: Docker login was not provided. ",
                         str(context.exception))

    def test_eq(self):
        docker_config_one = DockerConfig(self.valid_config)
        docker_config_two = DockerConfig(self.valid_config)

        self.assertEqual(docker_config_one, docker_config_two)

        docker_config_two = DockerConfig(self.no_registry_config)

        self.assertNotEqual(docker_config_one, docker_config_two)

        docker_config_two = GithubConfig(self.github_config)

        self.assertNotEqual(docker_config_one, docker_config_two)


class GithubConfigTest(unittest.TestCase):
    def setUp(self):
        self.valid_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password"
        }

        self.no_login_config = {
            "organization": "some_org",
            "password": "some_password"
        }

        self.no_password_config = {
            "organization": "some_org",
            "login": "some_login"
        }

        self.no_organization_config = {
            "login": "some_login",
            "password": "some_password"
        }

        self.docker_config = {
            "registry": "some_repo",
            "login": "some_login",
            "password": "some_password"
        }

    def test_valid_config(self):
        github_config = GithubConfig(self.valid_config)

        self.assertEqual(self.valid_config["organization"], github_config.organization)
        self.assertEqual(self.valid_config["login"], github_config.login)
        self.assertEqual(self.valid_config["password"], github_config.password)

    def test_no_password_config(self):
        github_config = GithubConfig(self.no_password_config)

        self.assertEqual(self.no_password_config["organization"], github_config.organization)
        self.assertEqual(self.no_password_config["login"], github_config.login)
        self.assertEqual("", github_config.password)

    def test_no_organization_config(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            GithubConfig(self.no_organization_config)

        self.assertEqual("InvalidRLIConfiguration has been raised: Github organization was not provided. ",
                         str(context.exception))

    def test_no_login_config(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            GithubConfig(self.no_login_config)

        # Don't forget the space at the end
        self.assertEqual("InvalidRLIConfiguration has been raised: Github login was not provided.",
                         str(context.exception))

    def test_eq(self):
        github_config_one = GithubConfig(self.valid_config)
        github_config_two = GithubConfig(self.valid_config)

        self.assertEqual(github_config_one, github_config_two)

        github_config_two = GithubConfig(self.no_password_config)

        self.assertNotEqual(github_config_one, github_config_two)

        github_config_two = DockerConfig(self.docker_config)

        self.assertNotEqual(github_config_one, github_config_two)


class RLIConfigTest(unittest.TestCase):
    def setUp(self):
        self.valid_config = {
            "github": {
                "organization": "some_org",
                "login": "some_login",
                "password": "some_password"
            },
            "docker": {
                "registry": "some_repo",
                "login": "some_login",
                "password": "some_password"
            }
        }

        self.no_github_config = {
            "docker": {
                "registry": "some_repo",
                "login": "some_login",
                "password": "some_password"
            }
        }

        self.no_docker_config = {
            "github": {
                "organization": "some_org",
                "login": "some_login",
                "password": "some_password"
            }
        }

    @mock.patch("json.load")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_valid_config(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config = RLIConfig()
        docker_config = DockerConfig(self.valid_config["docker"])
        github_config = GithubConfig(self.valid_config["github"])

        self.assertEqual(docker_config, rli_config.docker_config)
        self.assertEqual(github_config, rli_config.github_config)

    @mock.patch("json.load")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_no_github_config(self, mock_open, mock_load):
        mock_load.return_value = self.no_github_config
        mock_open.read_data = str(self.no_github_config)

        with self.assertRaises(InvalidRLIConfiguration) as context:
            RLIConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Github configuration was not provided in ~/.rli/config.json. ",
            str(context.exception))

    @mock.patch("json.load")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_no_docker_config(self, mock_open, mock_load):
        mock_load.return_value = self.no_docker_config
        mock_open.read_data = str(self.no_docker_config)

        with self.assertRaises(InvalidRLIConfiguration) as context:
            RLIConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Docker configuration was not provided in ~/.rli/config.json.",
            str(context.exception))

    @mock.patch("json.load")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_neq(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config = RLIConfig()
        docker_config = DockerConfig(self.valid_config["docker"])

        self.assertNotEqual(rli_config, docker_config)

    @mock.patch("json.load")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_eq(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config_one = RLIConfig()
        rli_config_two = RLIConfig()

        self.assertEqual(rli_config_one, rli_config_two)

    @mock.patch("json.load")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_get_config_or_exit_valid_config(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config = get_config_or_exit()
        docker_config = DockerConfig(self.valid_config["docker"])
        github_config = GithubConfig(self.valid_config["github"])

        self.assertEqual(docker_config, rli_config.docker_config)
        self.assertEqual(github_config, rli_config.github_config)

    @mock.patch("sys.exit")
    @mock.patch("builtins.open")
    @mock.patch("logging.exception")
    def test_get_config_or_exit_no_file(self, mock_logging_exception, mock_open, mock_exit):
        mock_open.side_effect = FileNotFoundError
        get_config_or_exit()

        self.assertEqual(ExitStatus.NO_RLI_CONFIG, mock_exit.call_args[0][0])
        self.assertTrue("Could not find ~/.rli/config.json", mock_logging_exception.call_args[0][0])

    @mock.patch("sys.exit")
    @mock.patch("json.load")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("logging.exception")
    def test_get_config_or_exit_invalid_config(self, mock_logging_exception, mock_open, mock_load, mock_exit):
        mock_load.return_value = self.no_docker_config
        mock_open.read_data = str(self.no_docker_config)
        get_config_or_exit()

        self.assertEqual(ExitStatus.INVALID_RLI_CONFIG, mock_exit.call_args[0][0])
        self.assertTrue("Your ~/.rli/config.json file is invalid.", mock_logging_exception.call_args[0][0])
        self.assertTrue("InvalidRLIConfiguration has been raised: Docker configuration was not provided in ~/.rli/config.json.", str(mock_logging_exception.call_args[0][1]))
