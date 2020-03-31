from rli import cli


def make_test_context(command_args):
    context = cli.cli.make_context(cli.cli, command_args)
    return context


class MockResponse:
    def __init__(self, status_code, json):
        self.ok = status_code == 200
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


class MockGithubConfig:
    def __init__(self, organization, username, login, password):
        self.organization = organization
        self.username = username
        self.login = login
        self.password = password


class MockDockerConfig:
    def __init__(self, registry, login, password):
        self.registry = registry
        self.login = login
        self.password = password
