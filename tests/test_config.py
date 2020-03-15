from unittest import mock
from rli.config import DockerConfig, GithubConfig, RLIConfig, get_rli_config_or_exit, DockerDeployConfig, DeployConfig
from rli.exceptions import InvalidRLIConfiguration, InvalidDeployConfiguration
from rli.constants import ExitStatus
from unittest.mock import patch
from unittest import TestCase


class DockerConfigTest(TestCase):
    def setUp(self):
        self.valid_config = {
            "registry": "some_repo",
            "login": "some_login",
            "password": "some_password"
        }

        self.valid_config_diff = {
            "registry": "some_rep",
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
        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig(self.no_registry_config)

        self.assertEqual("InvalidRLIConfiguration has been raised: Docker registry was not provided. ",
                         str(context.exception))

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

        docker_config_two = DockerConfig(self.valid_config_diff)

        self.assertNotEqual(docker_config_one, docker_config_two)

        docker_config_two = GithubConfig(self.github_config)

        self.assertNotEqual(docker_config_one, docker_config_two)


class GithubConfigTest(TestCase):
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


class RLIConfigTest(TestCase):
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

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_valid_config(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config = RLIConfig()
        docker_config = DockerConfig(self.valid_config["docker"])
        github_config = GithubConfig(self.valid_config["github"])

        self.assertEqual(docker_config, rli_config.docker_config)
        self.assertEqual(github_config, rli_config.github_config)

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_no_github_config(self, mock_open, mock_load):
        mock_load.return_value = self.no_github_config
        mock_open.read_data = str(self.no_github_config)

        with self.assertRaises(InvalidRLIConfiguration) as context:
            RLIConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Github configuration was not provided in ~/.rli/config.json. ",
            str(context.exception))

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_no_docker_config(self, mock_open, mock_load):
        mock_load.return_value = self.no_docker_config
        mock_open.read_data = str(self.no_docker_config)

        with self.assertRaises(InvalidRLIConfiguration) as context:
            RLIConfig()

        self.assertEqual(
            "InvalidRLIConfiguration has been raised: Docker configuration was not provided in ~/.rli/config.json.",
            str(context.exception))

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_neq(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config = RLIConfig()
        docker_config = DockerConfig(self.valid_config["docker"])

        self.assertNotEqual(rli_config, docker_config)

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_eq(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config_one = RLIConfig()
        rli_config_two = RLIConfig()

        self.assertEqual(rli_config_one, rli_config_two)

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_get_config_or_exit_valid_config(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config
        mock_open.read_data = str(self.valid_config)

        rli_config = get_rli_config_or_exit()
        docker_config = DockerConfig(self.valid_config["docker"])
        github_config = GithubConfig(self.valid_config["github"])

        self.assertEqual(docker_config, rli_config.docker_config)
        self.assertEqual(github_config, rli_config.github_config)

    @patch("sys.exit")
    @patch("builtins.open")
    @patch("logging.exception")
    def test_get_config_or_exit_no_file(self, mock_logging_exception, mock_open, mock_exit):
        mock_open.side_effect = FileNotFoundError
        get_rli_config_or_exit()

        self.assertEqual(ExitStatus.NO_RLI_CONFIG, mock_exit.call_args[0][0])
        self.assertTrue("Could not find ~/.rli/config.json", mock_logging_exception.call_args[0][0])

    @patch("sys.exit")
    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    @patch("logging.exception")
    def test_get_config_or_exit_invalid_config(self, mock_logging_exception, mock_open, mock_load, mock_exit):
        mock_load.return_value = self.no_docker_config
        mock_open.read_data = str(self.no_docker_config)
        get_rli_config_or_exit()

        self.assertEqual(ExitStatus.INVALID_RLI_CONFIG, mock_exit.call_args[0][0])
        self.assertTrue("Your ~/.rli/config.json file is invalid.", mock_logging_exception.call_args[0][0])
        self.assertTrue("InvalidRLIConfiguration has been raised: Docker configuration was not provided in ~/.rli/config.json.", str(mock_logging_exception.call_args[0][1]))


class DockerDeployConfigTest(TestCase):
    def setUp(self):
        self.valid_config = {
            "image": "this is an image",
            "compose_file": "deploy/compose.yml"
        }

        self.valid_config_no_compose = {
            "image": "this is another image"
        }

        self.invalid_config = {
            "compose_file": "deploy/compose.yml"
        }

        self.github_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password"
        }

    def test_valid_config(self):
        docker_deploy_config = DockerDeployConfig(self.valid_config)

        self.assertEqual(self.valid_config["compose_file"], docker_deploy_config.compose_file)
        self.assertEqual(self.valid_config["image"], docker_deploy_config.image)

    def test_valid_config_no_compose(self):
        docker_deploy_config = DockerDeployConfig(self.valid_config_no_compose)

        self.assertIsNone(docker_deploy_config.compose_file)
        self.assertEqual(self.valid_config_no_compose["image"], docker_deploy_config.image)

    def test_invalid_config(self):
        with self.assertRaises(InvalidDeployConfiguration) as context:
            DockerDeployConfig(self.invalid_config)

        self.assertEqual("InvalidDeployConfiguration has been raised: No docker image specified. ", str(context.exception))

    def test_eq(self):
        docker_deploy_config_one = DockerDeployConfig(self.valid_config)
        docker_deploy_config_two = DockerDeployConfig(self.valid_config)

        self.assertEqual(docker_deploy_config_one, docker_deploy_config_two)

        docker_deploy_config_two = DockerDeployConfig(self.valid_config_no_compose)

        self.assertNotEqual(docker_deploy_config_one, docker_deploy_config_two)

        github_config = GithubConfig(self.github_config)

        self.assertNotEqual(docker_deploy_config_one, github_config)


class DeployConfigTest(TestCase):
    def setUp(self):
        self.valid_config = {
            "secrets": [
                "THIS_IS_SECRET"
            ],
            "docker": {
                "image": "this is an image",
                "compose_file": "deploy/compose.yml"
            }
        }

        self.valid_config_no_secrets = {
            "docker": {
                "image": "this is an image",
                "compose_file": "deploy/compose.yml"
            }
        }

        self.invalid_config = {
            "secrets": [
                "THIS_IS_SECRET"
            ]
        }

        self.github_config = {
            "organization": "some_org",
            "login": "some_login",
            "password": "some_password"
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

        docker_deploy_config = DockerDeployConfig(self.valid_config_no_secrets["docker"])

        self.assertEqual(docker_deploy_config, deploy_config.docker_deploy_config)
        self.assertEqual([], deploy_config.secrets)

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_valid_config_no_secrets(self, mock_open, mock_load):
        mock_load.return_value = self.invalid_config
        mock_open.read_data = str(self.invalid_config)

        with self.assertRaises(InvalidDeployConfiguration) as context:
            DeployConfig()

        self.assertEqual("InvalidDeployConfiguration has been raised: No configuration specified.", str(context.exception))

    @patch("json.load")
    @patch("builtins.open", new_callable=mock.mock_open)
    def test_eq(self, mock_open, mock_load):
        mock_load.return_value = self.valid_config_no_secrets
        mock_open.read_data = str(self.valid_config_no_secrets)

        deploy_config_one = DeployConfig()
        deploy_config_two = DeployConfig()

        self.assertEqual(deploy_config_one, deploy_config_two)

        github_config = GithubConfig(self.github_config)

        self.assertNotEqual(deploy_config_one, github_config)
