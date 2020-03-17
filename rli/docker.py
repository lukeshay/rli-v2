import logging
import os
from rli.exceptions import RLIDockerException
from rli.utils.bash import Bash


class RLIDocker:
    def __init__(self, username, password, registry):
        self.username = username
        self.password = password
        self.registry = registry if registry[-1] == "/" else registry + "/"
        self.login()

    def login(self):
        if (
            Bash.run_command(
                [
                    "echo",
                    f'"{self.password}"',
                    "|",
                    "docker",
                    "login",
                    "-u",
                    self.username,
                    "--password-stdin",
                    self.registry,
                ]
            ).returncode
            != 0
        ):
            raise RLIDockerException("Could not log into the provided Docker registry.")

    def pull(self, image):
        """
        Pulls a image from the registry passed in to the constructor. E.g.
        image='ubuntu', docker pull some.registry.com/ubuntu
        :param image: The name of the image
        :return: The full image name if successful, otherwise None
        """
        if (
            Bash.run_command(["docker", "pull", f"{self.registry}{image}"]).returncode
            != 0
        ):
            return None
        else:
            return f"{self.registry}{image}"

    def tag(self, current_tag, new_tag):
        """
        Tags a docker images with the new tag.
        :param current_tag: The current tag
        :param new_tag: The new tag
        :return: The new tag if the command is successful, otherwise None
        """
        if Bash.run_command(["docker", "tag", current_tag, new_tag]).returncode != 0:
            return None
        else:
            return new_tag

    def compose_up(self, compose_file, secrets):
        """
        Runs docker-compose up for the given docker-compose file. The given
        secrets tuple is passed in as well.

        :param compose_file: The docker-compose file
        :param secrets: A dict of the secrets
        :return: The exit code of the cli command
        """
        return Bash.run_command(
            args=["docker-compose", "-f", compose_file, "up", "-d"], env=secrets
        ).returncode

    def run_image(self, image, secrets):
        """
        Runs a the Docker image you pass in along with the secrets as environment variables for Docker image.
        :param image: The name of the image
        :param secrets: The secrets to pass in
        :return: The exit code of the command
        """
        args = ["docker", "run", "-d"]

        for key, value in secrets.items():
            args.append("-e")
            args.append(f"{key}={value}")

        args.append(image)

        return Bash.run_command(args=args, env=secrets).returncode
