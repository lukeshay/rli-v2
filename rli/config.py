import json
import os
import sys
import logging
from rli.exceptions import InvalidRLIConfiguration
from rli.constants import ExitCode


class DockerConfig:
    def __init__(self, config):
        self.registry = config.get("registry") or None
        self.login = config.get("login") or None
        self.password = config.get("password") or None

        self.validate_config()

    def validate_config(self):
        message = ""

        if not self.registry:
            message += "Docker registry was not provided. "

        if not self.login:
            message += "Docker login was not provided. "

        if not self.password:
            message += "Docker password was not provided."

        if message != "":
            raise InvalidRLIConfiguration(message)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.registry == other.registry
                and self.login == other.login
                and self.password == other.password
            )

        return False


class GithubConfig:
    def __init__(self, config):
        self.organization = config.get("organization") or None
        self.login = config.get("login") or None
        self.password = config.get("password") or None

        self.validate_config()

    def validate_config(self):
        message = ""

        if not self.organization:
            message += "Github organization was not provided. "

        if not self.login:
            message += "Github login was not provided."

        if not self.password:
            self.password = ""

        if message != "":
            raise InvalidRLIConfiguration(message)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.organization == other.organization
                and self.login == other.login
                and self.password == other.password
            )

        return False


class RLIConfig:
    def __init__(self):
        self.home_dir = os.path.expanduser("~")

        self.rli_config = self.load_rli_config()
        self.rli_secrets = self.load_rli_secrets()

        self._github_config = None
        self._docker_config = None

    @property
    def github_config(self) -> GithubConfig:
        if self._github_config is None:
            github_config = self.rli_config.get("github") or None

            if not github_config:
                raise InvalidRLIConfiguration(
                    "Github configuration was not provided in ~/.rli/config.json."
                )

            self._github_config = GithubConfig(github_config)

        return self._github_config

    @property
    def docker_config(self) -> DockerConfig:
        if self._docker_config is None:
            docker_config = self.rli_config.get("docker") or None

            if not docker_config:
                raise InvalidRLIConfiguration(
                    "Docker configuration was not provided in ~/.rli/config.json."
                )

            self._docker_config = DockerConfig(docker_config)

        return self._docker_config

    def get_secret(self, key):
        value = ""
        try:
            value = self.rli_secrets[key]
        except KeyError:
            pass

        return value

    def load_rli_config(self):
        config = {}
        with open(f"{self.home_dir}/.rli/config.json", "r") as config:
            config = json.load(config)

        return config

    def load_rli_secrets(self):
        secrets = {}
        with open(f"{self.home_dir}/.rli/secrets.json", "r") as secrets:
            secrets = json.load(secrets)

        return secrets

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.github_config == other.github_config
                and self.docker_config == other.docker_config
            )

        return False


def get_rli_config_or_exit() -> RLIConfig:
    config = None
    try:
        config = RLIConfig()
    # except InvalidRLIConfiguration as e:
    #     logging.exception("Your ~/.rli/config.json file is invalid.", e)
    #     sys.exit(ExitCode.INVALID_RLI_CONFIG)
    except FileNotFoundError:
        logging.exception("Could not find ~/.rli/config.json.")
        sys.exit(ExitCode.NO_RLI_CONFIG)

    return config
