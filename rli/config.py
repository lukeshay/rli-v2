import json
import os
import sys
import logging
from rli.exceptions import InvalidRLIConfiguration
from rli.constants import ExitStatus


class DockerConfig:
    def __init__(self, config):
        try:
            self.registry = config["registry"]
        except KeyError:
            self.registry = ""

        try:
            self.login = config["login"]
        except KeyError:
            self.login = None

        try:
            self.password = config["password"]
        except KeyError:
            self.password = None

        self.validate_config()

    def validate_config(self):
        message = ""

        if not self.registry:
            self.registry = ""

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
        else:
            return False


class GithubConfig:
    def __init__(self, config):
        try:
            self.organization = config["organization"]
        except KeyError:
            self.organization = None

        try:
            self.login = config["login"]
        except KeyError:
            self.login = None

        try:
            self.password = config["password"]
        except KeyError:
            self.password = None

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
        else:
            return False


class RLIConfig:
    def __init__(self):
        self.home_dir = os.path.expanduser("~")

        self.rli_config_path = f"{self.home_dir}/.rli/config.json"
        with open(self.rli_config_path, "r") as config:
            self.rli_config = json.load(config)

        self.rli_vars_path = f"{self.home_dir}/.rli/vars.json"
        with open(self.rli_vars_path, "r") as config:
            self.rli_vars = json.load(config)

        message = ""

        try:
            self.rli_config["github"]
        except KeyError:
            message += "Github configuration was not provided in ~/.rli/config.json. "

        try:
            self.rli_config["docker"]
        except KeyError:
            message += "Docker configuration was not provided in ~/.rli/config.json."

        if message != "":
            raise InvalidRLIConfiguration(message)

        self.github_config = GithubConfig(self.rli_config["github"])
        self.docker_config = DockerConfig(self.rli_config["docker"])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.github_config == other.github_config
                and self.docker_config == other.docker_config
            )
        else:
            return False


def get_config_or_exit():
    config = None
    try:
        config = RLIConfig()
    except InvalidRLIConfiguration as e:
        logging.exception("Your ~/.rli/config.json file is invalid.", e)
        sys.exit(ExitStatus.INVALID_RLI_CONFIG)
    except FileNotFoundError:
        logging.exception("Could not find ~/.rli/config.json")
        sys.exit(ExitStatus.NO_RLI_CONFIG)

    return config
