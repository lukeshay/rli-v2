from github import Github, GithubException
import logging


class RLIGithub:
    def __init__(self, config):
        self.github = (
            Github(config.login, config.password)
            if config.password
            else Github(config.login)
        )
        self.config = config

    def create_repo(self, repo_name, repo_description="", private="false"):
        logging.debug(f"Creating repo '{repo_name}'.")
        private = private == "true"

        try:
            return self.github.get_user().create_repo(
                repo_name,
                description=repo_description,
                private=private,
                auto_init=True,
            )
        except GithubException as e:
            if e.status == 422:
                logging.error("Repository name is taken.")
            else:
                logging.error("There was an exception when creating your repository.")
