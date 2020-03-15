# from github import Github
#
#
# class RLIGithub:
#     def __init__(self, login, password=None):
#         self.github = Github(login, password) if password else Github(username)
#
#     def create_repo(self, repo_name, description="", private=False):
#         self.github.get_user().create_repo()