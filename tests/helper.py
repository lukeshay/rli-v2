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
