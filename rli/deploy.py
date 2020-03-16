from rli.docker import RLIDocker
from rli.config import DockerDeployConfig, DockerConfig, RLIConfig, DeployConfig
import logging


class RLIDeploy:
    def __init__(self, rli_config, deploy_config):
        self._rli_config = rli_config
        self._deploy_config = deploy_config

        self._rli_docker = None

    def run_deploy(self, commit):
        if self.docker_deploy_config():
            commit = "latest" if commit == "master" else commit

            image = self.rli_docker().pull(
                f"{self.docker_deploy_config().image}:{commit}"
            )

            if not image:
                return

            tag = self.rli_docker().tag(
                image, f"{self.docker_deploy_config().image}:{commit}"
            )

            if not tag:
                return

            if self.docker_deploy_config().compose_file:
                self.rli_docker().compose_up(
                    self.docker_deploy_config().compose_file,
                    self.rli_config().rli_secrets,
                )
            else:
                self.rli_docker().run_image(
                    self.docker_deploy_config().image, self.rli_config().rli_secrets,
                )

    # These methods are used for improved intellisense
    def docker_deploy_config(self) -> DockerDeployConfig:
        return self.deploy_config().docker_deploy_config

    def docker_config(self) -> DockerConfig:
        return self.rli_config().docker_config

    def rli_config(self) -> RLIConfig:
        return self._rli_config

    def deploy_config(self) -> DeployConfig:
        return self._deploy_config

    def rli_docker(self) -> RLIDocker:
        if not self._rli_docker:
            self._rli_docker = RLIDocker(
                self.docker_config().login,
                self.docker_config().password,
                self.docker_config().registry,
            )

        return self._rli_docker
