from rli import cli


def make_test_context(command_args):
    context = cli.cli.make_context(cli.cli, command_args)
    return context
