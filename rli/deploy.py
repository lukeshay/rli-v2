from rli.docker import RLIDocker
from rli.config import (
    DockerDeployConfig,
    DockerConfig,
    DeployConfig,
    RLISecrets,
    get_deploy_config_or_exit,
    get_docker_config_or_exit,
)
import logging


class RLIDeploy:
    def __init__(self):
        self._deploy_config = get_deploy_config_or_exit()
        self._rli_docker = None
        self.rli_secrets = RLISecrets()

    def run_deploy(self, commit):
        if self.docker_deploy_config:
            logging.debug(f"Running Docker deploy for commit: {commit}")
            commit = "latest" if commit == "master" else commit

            image = self.rli_docker.pull(f"{self.docker_deploy_config.image}:{commit}")

            if not image:
                logging.error("There was an error pulling the docker image.")
                return

            tag = self.rli_docker.tag(
                image, f"{self.docker_deploy_config.image}:latest"
            )

            if not tag:
                logging.error("There was an error tagging the docker image.")
                return

            if self.docker_deploy_config.compose_file:
                return self.rli_docker.compose_up(
                    self.docker_deploy_config.compose_file, self.rli_secrets,
                )
            else:
                return self.rli_docker.run_image(
                    f"{self.docker_deploy_config.image}:latest", self.rli_secrets,
                )

    # These methods are used for improved intellisense
    @property
    def docker_deploy_config(self) -> DockerDeployConfig:
        return self.deploy_config.docker_deploy_config

    @property
    def docker_config(self) -> DockerConfig:
        if not self._rli_docker:
            self._rli_docker = get_docker_config_or_exit()

        return self._rli_docker

    @property
    def deploy_config(self) -> DeployConfig:
        return self._deploy_config

    @property
    def rli_docker(self) -> RLIDocker:
        if not self._rli_docker:
            self._rli_docker = RLIDocker()

        return self._rli_docker
