class RLIDeploy:
    def __init__(self, deploy_config):
        self.deploy_config = deploy_config
        self.docker_deploy_config = None

    def run_deploy(self):
        if self.deploy_config.docker_deploy_config:
            self.docker_deploy_config = self.deploy_config.docker_deploy_config
