import click
from rli.cli import CONTEXT_SETTINGS


@click.group(name="git", help="Contains all git commands for RLI.")
@click.pass_context
def cli(cts):
    pass


@cli.command(
    name="create-repo",
    context_settings=CONTEXT_SETTINGS,
    help="Creates a repo with the given information",
)
@click.pass_context
def create_repo(ctx):
    print("Creating repo")
