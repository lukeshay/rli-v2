from rli import cli


def make_test_context(command_args):
    context = cli.rli.make_context(cli.rli, command_args)
    return context
