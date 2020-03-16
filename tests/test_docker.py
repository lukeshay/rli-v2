from rli.docker import RLIDocker
from unittest import TestCase
from unittest.mock import Mock
from rli.exceptions import RLIDockerException
from rli.utils import bash
import subprocess
import os


class RLIDockerTest(TestCase):
    def setUp(self):
        self.username = "some username"
        self.registry = "some.registry/"
        self.registry_no_trailing_slash = "some.registry"
        self.password = "some password"
        self.image = "some-image-name:latest"
        self.image_tag = "some-image-name:asdf"
        self.compose_file = "deploy/deploy.json"
        self.secrets = {"SECRET_ONE": "secret one", "SECRET_TWO": "secret two"}
        self.env = os.environ
        self.env.update(self.secrets)

        self.mock_subprocess_run_return = Mock()
        self.mock_subprocess_run_return.returncode = 0

        self.mock_subprocess_run = Mock()
        self.mock_subprocess_run.return_value = self.mock_subprocess_run_return

        bash.subprocess.run = self.mock_subprocess_run

    def set_subprocess_returncode(self, code):
        self.mock_subprocess_run_return.returncode = code

    def construct_rli_docker(self):
        rli_docker = RLIDocker(self.username, self.password, self.registry)

        self.mock_subprocess_run.assert_called_with(
            args=[
                "echo",
                f'"{self.password}"',
                "|",
                "docker",
                "login",
                "-u",
                self.username,
                "--password-stdin",
                self.registry,
            ],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        return rli_docker

    def test_construct_successful_login(self):
        rli_docker = RLIDocker(self.username, self.password, self.registry)

        self.assertEqual(self.username, rli_docker.username)
        self.assertEqual(self.password, rli_docker.password)
        self.assertEqual(self.registry, rli_docker.registry)
        self.mock_subprocess_run.assert_called_with(
            args=[
                "echo",
                f'"{self.password}"',
                "|",
                "docker",
                "login",
                "-u",
                self.username,
                "--password-stdin",
                self.registry,
            ],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        rli_docker = RLIDocker(
            self.username, self.password, self.registry_no_trailing_slash
        )

        self.assertEqual(self.username, rli_docker.username)
        self.assertEqual(self.password, rli_docker.password)
        self.assertEqual(self.registry, rli_docker.registry)
        self.mock_subprocess_run.assert_called_with(
            args=[
                "echo",
                f'"{self.password}"',
                "|",
                "docker",
                "login",
                "-u",
                self.username,
                "--password-stdin",
                self.registry,
            ],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    def test_construct_unsuccessful_login(self):
        self.set_subprocess_returncode(1)

        with self.assertRaises(RLIDockerException) as context:
            RLIDocker(self.username, self.password, self.registry)

        self.assertEqual(
            "RLIDockerException has been raised: Could not log into the provided Docker registry.",
            str(context.exception),
        )
        self.mock_subprocess_run.assert_called_with(
            args=[
                "echo",
                f'"{self.password}"',
                "|",
                "docker",
                "login",
                "-u",
                self.username,
                "--password-stdin",
                self.registry,
            ],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

    def test_successful_pull(self):
        rli_docker = self.construct_rli_docker()

        pull = rli_docker.pull(self.image)

        self.mock_subprocess_run.assert_called_with(
            args=["docker", "pull", f"{self.registry}{self.image}"],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(f"{self.registry}{self.image}", pull)

    def test_unsuccessful_pull(self):
        rli_docker = self.construct_rli_docker()

        self.set_subprocess_returncode(1)

        pull = rli_docker.pull(self.image)

        self.mock_subprocess_run.assert_called_with(
            args=["docker", "pull", f"{self.registry}{self.image}"],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertIsNone(pull)

    def test_successful_tag(self):
        rli_docker = self.construct_rli_docker()

        tag = rli_docker.tag(self.image, self.image_tag)

        self.mock_subprocess_run.assert_called_with(
            args=["docker", "tag", self.image, self.image_tag],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(self.image_tag, tag)

    def test_unsuccessful_tag(self):
        rli_docker = self.construct_rli_docker()

        self.set_subprocess_returncode(1)

        tag = rli_docker.tag(self.image, self.image_tag)

        self.mock_subprocess_run.assert_called_with(
            args=["docker", "tag", self.image, self.image_tag],
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertIsNone(tag)

    def test_successful_compose_up(self):
        rli_docker = self.construct_rli_docker()

        compose_up = rli_docker.compose_up(self.compose_file, self.secrets)

        args = ["docker-compose", "-f", self.compose_file, "up", "-d"]

        self.mock_subprocess_run.assert_called_with(
            args=args,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, compose_up)

    def test_unsuccessful_compose_up(self):
        rli_docker = self.construct_rli_docker()

        self.set_subprocess_returncode(1)

        compose_up = rli_docker.compose_up(self.compose_file, self.secrets)

        args = ["docker-compose", "-f", self.compose_file, "up", "-d"]

        self.mock_subprocess_run.assert_called_with(
            args=args,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(1, compose_up)

    def test_successful_run_image(self):
        rli_docker = self.construct_rli_docker()

        run_image = rli_docker.run_image(self.image, self.secrets)

        args = ["docker", "run", "-d"]

        for key, value in self.secrets.items():
            args.append("-e")
            args.append(f"{key}={value}")

        args.append(self.image)

        self.mock_subprocess_run.assert_called_with(
            args=args,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, run_image)

    def test_unsuccessful_run_image(self):
        rli_docker = self.construct_rli_docker()

        self.set_subprocess_returncode(1)

        run_image = rli_docker.run_image(self.image, self.secrets)

        args = ["docker", "run", "-d"]

        for key, value in self.secrets.items():
            args.append("-e")
            args.append(f"{key}={value}")

        args.append(self.image)

        self.mock_subprocess_run.assert_called_with(
            args=args,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(1, run_image)
