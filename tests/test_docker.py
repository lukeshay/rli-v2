from rli.docker import RLIDocker
from rli import docker
from unittest import TestCase
from unittest.mock import Mock, patch
from rli.exceptions import RLIDockerException


class RLIDockerTest(TestCase):
    def setUp(self):
        self.username = "some username"
        self.registry = "some.registry/"
        self.registry_no_trailing_slash = "some.registry"
        self.password = "some password"
        self.image = "some-image-name:latest"
        self.image_tag = "some-image-name:asdf"
        self.compose_file = "deploy/deploy.json"
        self.secrets = [
            ("SECRET_ONE", "secret one"),
            ("SECRET_TWO", "secret two")
        ]

        self.mock_subprocess_run_return = Mock()
        self.mock_subprocess_run_return.returncode = 0

        self.mock_subprocess_run = Mock()
        self.mock_subprocess_run.return_value = self.mock_subprocess_run_return

        docker.subprocess.run = self.mock_subprocess_run

    def set_subprocess_returncode(self, code):
        self.mock_subprocess_run_return.returncode = code

    def construct_rli_docker(self):
        rli_docker = RLIDocker(self.username, self.password, self.registry)

        self.mock_subprocess_run.assert_called_with([
            "echo",
            f'"{self.password}"',
            "|",
            "docker",
            "login",
            "-u",
            self.username,
            "--password-stdin",
            self.registry,
        ])

        return rli_docker

    def test_construct_successful_login(self):
        rli_docker = RLIDocker(self.username, self.password, self.registry)

        self.assertEqual(self.username, rli_docker.username)
        self.assertEqual(self.password, rli_docker.password)
        self.assertEqual(self.registry, rli_docker.registry)
        self.mock_subprocess_run.assert_called_with([
            "echo",
            f'"{self.password}"',
            "|",
            "docker",
            "login",
            "-u",
            self.username,
            "--password-stdin",
            self.registry,
        ])

        rli_docker = RLIDocker(self.username, self.password, self.registry_no_trailing_slash)

        self.assertEqual(self.username, rli_docker.username)
        self.assertEqual(self.password, rli_docker.password)
        self.assertEqual(self.registry, rli_docker.registry)
        self.mock_subprocess_run.assert_called_with([
            "echo",
            f'"{self.password}"',
            "|",
            "docker",
            "login",
            "-u",
            self.username,
            "--password-stdin",
            self.registry,
        ])

    def test_construct_unsuccessful_login(self):
        self.set_subprocess_returncode(1)

        with self.assertRaises(RLIDockerException) as context:
            RLIDocker(self.username, self.password, self.registry)

        self.assertEqual("RLIDockerException has been raised: Could not log into the provided Docker registry.", str(context.exception))
        self.mock_subprocess_run.assert_called_with([
            "echo",
            f'"{self.password}"',
            "|",
            "docker",
            "login",
            "-u",
            self.username,
            "--password-stdin",
            self.registry,
        ])

    def test_successful_pull(self):
        rli_docker = self.construct_rli_docker()

        pull = rli_docker.pull(self.image)

        self.mock_subprocess_run.assert_called_with(["docker", "pull", f"{self.registry}{self.image}"])
        self.assertEqual(f"{self.registry}{self.image}", pull)

    def test_unsuccessful_pull(self):
        rli_docker = self.construct_rli_docker()

        self.set_subprocess_returncode(1)

        pull = rli_docker.pull(self.image)

        self.mock_subprocess_run.assert_called_with(["docker", "pull", f"{self.registry}{self.image}"])
        self.assertIsNone(pull)

    def test_successful_tag(self):
        rli_docker = self.construct_rli_docker()

        tag = rli_docker.tag(self.image, self.image_tag)

        self.mock_subprocess_run.assert_called_with(["docker", "tag", self.image, self.image_tag])
        self.assertEqual(self.image_tag, tag)

    def test_unsuccessful_tag(self):
        rli_docker = self.construct_rli_docker()

        self.set_subprocess_returncode(1)

        tag = rli_docker.tag(self.image, self.image_tag)

        self.mock_subprocess_run.assert_called_with(["docker", "tag", self.image, self.image_tag])
        self.assertIsNone(tag)

    def test_successful_compose_up(self):
        rli_docker = self.construct_rli_docker()

        compose_up = rli_docker.compose_up(self.compose_file, self.secrets)

        args = []

        for secret in self.secrets:
            args.append(f"{secret[0]}={secret[1]}")

        args.append("docker-compose")
        args.append("-f")
        args.append(self.compose_file)
        args.append("up")
        args.append("-d")

        self.mock_subprocess_run.assert_called_with(args)
        self.assertEqual(0, compose_up)

    def test_unsuccessful_compose_up(self):
        rli_docker = self.construct_rli_docker()

        self.set_subprocess_returncode(1)

        compose_up = rli_docker.compose_up(self.compose_file, self.secrets)

        args = []

        for secret in self.secrets:
            args.append(f"{secret[0]}={secret[1]}")

        args.append("docker-compose")
        args.append("-f")
        args.append(self.compose_file)
        args.append("up")
        args.append("-d")

        self.mock_subprocess_run.assert_called_with(args)
        self.assertEqual(1, compose_up)
