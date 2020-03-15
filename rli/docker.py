import subprocess
from rli.exceptions import RLIDockerException


class RLIDocker:
    def __init__(self, username, password, registry):
        self.username = username
        self.password = password
        self.registry = registry if registry[-1] == "/" else registry + "/"
        self.login()

    def login(self):
        if (
            subprocess.run(
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
        if subprocess.run(["docker", "pull", f"{self.registry}{image}"]) != 0:
            return None
        else:
            return f"{self.registry}/{image}"

    def tag(self, current_tag, new_tag):
        """
        Tags a docker images with the new tag.
        :param current_tag: The current tag
        :param new_tag: The new tag
        :return: The new tag if the command is successful, otherwise None
        """
        if subprocess.run(["docker", "tag", current_tag, new_tag]) != 0:
            return None
        else:
            return new_tag

    def compose_up(self, compose_file, secrets):
        """
        Runs docker-compose up for the given docker-compose file. The given
        secrets tuple is passed in as well.

        :param compose_file: The docker-compose file
        :param secrets: An array of key, value pair tuples. E.g. [("key", "value")]
        :return: The exit code of the cli command
        """
        args = []

        for secret in secrets:
            args.append(f"{secret[0]}={secret[1]}")

        return subprocess.run(["docker-compose", "-f", {compose_file}, "up", "-d"])
