import click
import logging
import sys
from rli.cli import CONTEXT_SETTINGS
from rli.constants import ExitCode


@click.command(
    "smoke",
    context_settings=CONTEXT_SETTINGS,
    help="Command to run to make sure RLI is installed.",
)
@click.pass_context
def cli(ctx):
    logging.info("RLI is working properly.")
    sys.exit(ExitCode.OK)
