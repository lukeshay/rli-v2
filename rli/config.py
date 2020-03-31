import json
import sys
import logging
from rli.utils import bash
from rli.exceptions import InvalidRLIConfiguration, InvalidDeployConfiguration
from rli.constants import ExitCode


class DockerDeployConfig:
    def __init__(self, config):
        self.image = config.get("image", None)
        self.compose_file = config.get("compose_file", None)
        self.validate_config()

    def validate_config(self):
        message = ""

        if not self.image:
            message += "No docker image specified. "

        if message != "":
            raise InvalidDeployConfiguration(message)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.image == other.image and self.compose_file == other.compose_file

        return False


class DeployConfig:
    def __init__(self):
        with open("deploy/deploy.json", "r") as config:
            self.deploy_config = json.load(config)

        try:
            self._docker_deploy_config = DockerDeployConfig(
                self.deploy_config["docker"]
            )
        except KeyError:
            self._docker_deploy_config = None

        self.validate_config()

    @property
    def secrets(self):
        return self.deploy_config.get("secrets", [])

    @property
    def docker_deploy_config(self) -> DockerDeployConfig:
        return self._docker_deploy_config

    def validate_config(self):
        if not self.docker_deploy_config:
            raise InvalidDeployConfiguration("No configuration specified.")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.docker_deploy_config == other.docker_deploy_config
                and self.secrets == other.secrets
            )

        return False


class DockerConfig:
    def __init__(self):
        self.config = load_config().get("docker", None)
        self.validate_config()

    def validate_config(self):
        message = ""

        if "registry" not in self.config:
            message += "Docker registry was not provided. "

        if "login" not in self.config:
            message += "Docker login was not provided. "

        if "password" not in self.config:
            message += "Docker password was not provided."

        if message != "":
            raise InvalidRLIConfiguration(message)

    @property
    def registry(self):
        return self.config.get("registry", "")

    @property
    def login(self):
        return self.config.get("login", "")

    @property
    def password(self):
        return self.config.get("password", "")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.registry == other.registry
                and self.login == other.login
                and self.password == other.password
            )

        return False


class GithubConfig:
    def __init__(self):
        self.config = load_config().get("github", None)
        self.validate_config()

    def validate_config(self):
        message = ""

        if not self.config:
            raise InvalidRLIConfiguration("Not Github configuration found.")

        if "organization" not in self.config and "username" not in self.config:
            message += "Github organization or username was not provided. "

        if "login" not in self.config:
            message += "Github login was not provided."

        if message != "":
            raise InvalidRLIConfiguration(message)

    @property
    def organization(self) -> str:
        return self.config.get("organization", "")

    @property
    def username(self) -> str:
        return self.config.get("username", "")

    @property
    def login(self) -> str:
        return self.config.get("login", "")

    @property
    def password(self) -> str:
        return self.config.get("password", "")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.organization == other.organization
                and self.username == other.username
                and self.login == other.login
                and self.password == other.password
            )

        return False


class RLISecrets:
    def __init__(self):
        try:
            with open(f"{bash.home_dir()}/.rli/secrets.json") as secrets:
                self.secrets = json.load(secrets)
        except FileNotFoundError:
            self.secrets = {}

    def get_secret(self, secret):
        return self.secrets.get(secret, None)


def load_config() -> dict:
    with open(f"{bash.home_dir()}/.rli/config.json", "r") as config:
        config = json.load(config)

    return config


def get_github_config_or_exit() -> GithubConfig:
    try:
        return GithubConfig()
    except InvalidRLIConfiguration:
        logging.exception("Your Github config in ~/.rli/config.json is invalid.")
        sys.exit(ExitCode.INVALID_RLI_CONFIG)
    except FileNotFoundError:
        logging.exception("Could not find ~/.rli/config.json.")
        sys.exit(ExitCode.NO_RLI_CONFIG)


def get_docker_config_or_exit() -> DockerConfig:
    try:
        return DockerConfig()
    except InvalidRLIConfiguration:
        logging.exception("Your Docker config in ~/.rli/config.json is invalid.")
        sys.exit(ExitCode.INVALID_RLI_CONFIG)
    except FileNotFoundError:
        logging.exception("Could not find ~/.rli/config.json.")
        sys.exit(ExitCode.NO_RLI_CONFIG)


def get_deploy_config_or_exit() -> DeployConfig:
    try:
        return DeployConfig()
    except InvalidDeployConfiguration:
        logging.exception("Your config/config.json file is invalid.")
        sys.exit(ExitCode.INVALID_DEPLOY_CONFIG)
    except FileNotFoundError:
        logging.exception("Could not find config/config.json.")
        sys.exit(ExitCode.NO_DEPLOY_JSON)
