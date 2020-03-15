from github import Github


class RLIGithub:
    def __init__(self, config):
        self.github = (
            Github(config.login, config.password)
            if config.password
            else Github(config.login)
        )
        self.config = config

    def create_repo(self, repo_name, repo_description="", private="false"):
        private = private == "true"
        self.github.get_user().create_repo(
            repo_name,
            description=repo_description,
            private=private,
            auto_init=True,
        )
