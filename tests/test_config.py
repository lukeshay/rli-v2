import unittest
from rli.config import DockerConfig
from rli.exceptions import InvalidRLIConfiguration


class DockerConfigTest(unittest.TestCase):
    def setUp(self) -> None:
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

    def test_valid_config(self):
        docker_config = DockerConfig(self.valid_config)
        
        self.assertEqual(self.valid_config["registry"], docker_config.registry)
        self.assertEqual(self.valid_config["login"], docker_config.login)
        self.assertEqual(self.valid_config["password"], docker_config.password)

    def test_no_registry_config(self):
        docker_config = DockerConfig(self.no_registry_config)

        self.assertEqual("", docker_config.registry)
        self.assertEqual(self.valid_config["login"], docker_config.login)
        self.assertEqual(self.valid_config["password"], docker_config.password)

    def test_no_password_config(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig(self.no_password_config)

        self.assertEqual("InvalidRLIConfiguration has been raised: Docker password was not provided.", str(context.exception))

    def test_no_login_config(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            DockerConfig(self.no_login_config)

        # Don't forget the space at the end
        self.assertEqual("InvalidRLIConfiguration has been raised: Docker login was not provided. ", str(context.exception))
