from rli.deploy import RLIDeploy
from rli.utils import bash
from unittest import TestCase
from unittest.mock import Mock, patch
import os
import subprocess


# TODO(Luke): Assert logging messages
class DeployTest(TestCase):
    def setUp(self):
        self.login = "some username"
        self.password = "some password"
        self.registry = "some.registry/"

        self.mock_rli_config = Mock()

        # Mock rli config
        self.mock_docker_config = Mock()
        self.mock_rli_secrets = Mock()
        self.mock_docker_config.login = self.login
        self.mock_docker_config.password = self.password
        self.mock_docker_config.registry = self.registry
        self.mock_rli_config.docker_config = self.mock_docker_config
        self.mock_rli_config.rli_secrets = self.mock_rli_secrets

        # Mock deploy config
        self.image_name = "some_image_name"
        self.compose_file = "deploy/docker-compose.yml"
        self.mock_deploy_config = Mock()
        self.mock_docker_deploy_config = Mock()
        self.mock_docker_deploy_config.image = self.image_name
        self.mock_docker_deploy_config.compose_file = None
        self.mock_deploy_config.docker_deploy_config = self.mock_docker_deploy_config

        # Mock subprocess run
        self.mock_subprocess_run_return = Mock()
        self.mock_subprocess_run = Mock()
        self.mock_subprocess_run_return.returncode = 0
        self.mock_subprocess_run.return_value = self.mock_subprocess_run_return
        bash.subprocess.run = self.mock_subprocess_run

        self.rli_deploy = RLIDeploy(self.mock_rli_config, self.mock_deploy_config)

    def test_helper_methods(self):
        self.assertEqual(self.mock_rli_config, self.rli_deploy.rli_config)
        self.assertEqual(self.mock_docker_config, self.rli_deploy.docker_config)
        self.assertEqual(self.mock_deploy_config, self.rli_deploy.deploy_config)
        self.assertEqual(
            self.mock_docker_deploy_config, self.rli_deploy.docker_deploy_config
        )

        # This tests when rli_deploy._rli_deploy is None
        rli_docker_first_call = self.rli_deploy.rli_docker
        self.assertIsNotNone(rli_docker_first_call)

        # This tests when rli_deploy._rli_deploy is Some
        self.assertEqual(rli_docker_first_call, self.rli_deploy.rli_docker)

        self.mock_subprocess_run.assert_called_once()
        self.mock_subprocess_run.assert_called_with(
            args=[
                "echo",
                f'"{self.password}"',
                "|",
                "docker",
                "login",
                "-u",
                self.login,
                "--password-stdin",
                self.registry,
            ],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    @patch("rli.deploy.RLIDocker.compose_up")
    @patch("rli.deploy.RLIDocker.run_image")
    @patch("rli.deploy.RLIDocker.tag")
    @patch("rli.deploy.RLIDocker.pull")
    def test_run_deploy_docker_image(
        self, mock_pull, mock_tag, mock_run_image, mock_compose_up
    ):
        mock_pull.return_value = self.registry + self.image_name
        mock_tag.return_value = self.image_name + ":latest"
        mock_run_image.return_value = 0

        ret = self.rli_deploy.run_deploy("master")

        self.assertEqual(0, ret)
        mock_pull.assert_called_with(f"{self.image_name}:latest")
        mock_tag.assert_called_with(
            self.registry + self.image_name, f"{self.image_name}:latest"
        )
        mock_run_image.assert_called_with(
            f"{self.image_name}:latest", self.mock_rli_secrets
        )
        mock_compose_up.assert_not_called()

    @patch("rli.deploy.RLIDocker.compose_up")
    @patch("rli.deploy.RLIDocker.run_image")
    @patch("rli.deploy.RLIDocker.tag")
    @patch("rli.deploy.RLIDocker.pull")
    def test_run_deploy_docker_compose(
        self, mock_pull, mock_tag, mock_run_image, mock_compose_up
    ):
        self.mock_docker_deploy_config.compose_file = self.compose_file

        mock_pull.return_value = self.registry + self.image_name
        mock_tag.return_value = self.image_name + ":latest"
        mock_compose_up.return_value = 0

        ret = self.rli_deploy.run_deploy("master")

        self.assertEqual(0, ret)
        mock_pull.assert_called_with(f"{self.image_name}:latest")
        mock_tag.assert_called_with(
            self.registry + self.image_name, f"{self.image_name}:latest"
        )
        mock_compose_up.assert_called_with(self.compose_file, self.mock_rli_secrets)
        mock_run_image.assert_not_called()

    @patch("logging.error")
    @patch("rli.deploy.RLIDocker.compose_up")
    @patch("rli.deploy.RLIDocker.run_image")
    @patch("rli.deploy.RLIDocker.tag")
    @patch("rli.deploy.RLIDocker.pull")
    def test_run_deploy_pull_fail(
        self, mock_pull, mock_tag, mock_run_image, mock_compose_up, mock_logging_error
    ):
        mock_pull.return_value = None

        ret = self.rli_deploy.run_deploy("09asdf99")

        self.assertIsNone(ret)
        mock_pull.assert_called_with(f"{self.image_name}:09asdf99")
        mock_tag.assert_not_called()
        mock_run_image.assert_not_called()
        mock_compose_up.assert_not_called()
        mock_logging_error.assert_called_with(
            "There was an error pulling the docker image."
        )

    @patch("logging.error")
    @patch("rli.deploy.RLIDocker.compose_up")
    @patch("rli.deploy.RLIDocker.run_image")
    @patch("rli.deploy.RLIDocker.tag")
    @patch("rli.deploy.RLIDocker.pull")
    def test_run_deploy_tag_fail(
        self, mock_pull, mock_tag, mock_run_image, mock_compose_up, mock_logging_error
    ):
        mock_pull.return_value = self.registry + self.image_name
        mock_tag.return_value = None

        ret = self.rli_deploy.run_deploy("09asdf99")

        self.assertIsNone(ret)
        mock_pull.assert_called_with(f"{self.image_name}:09asdf99")
        mock_tag.assert_called_with(
            self.registry + self.image_name, f"{self.image_name}:latest"
        )
        mock_run_image.assert_not_called()
        mock_compose_up.assert_not_called()
        mock_logging_error.assert_called_with(
            "There was an error tagging the docker image."
        )

    @patch("rli.deploy.RLIDocker.compose_up")
    @patch("rli.deploy.RLIDocker.run_image")
    @patch("rli.deploy.RLIDocker.tag")
    @patch("rli.deploy.RLIDocker.pull")
    def test_run_deploy_not_docker(
        self, mock_pull, mock_tag, mock_run_image, mock_compose_up,
    ):
        self.mock_deploy_config.docker_deploy_config = None

        ret = self.rli_deploy.run_deploy("09asdf99")

        self.assertIsNone(ret)
        mock_pull.assert_not_called()
        mock_tag.assert_not_called()
        mock_run_image.assert_not_called()
        mock_compose_up.assert_not_called()
