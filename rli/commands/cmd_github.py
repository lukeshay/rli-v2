import click
import sys
import logging
from rli.cli import CONTEXT_SETTINGS
from rli.github import RLIGithub
from rli.config import get_rli_config_or_exit
from rli.constants import ExitCode


@click.group(name="github", help="Contains all github commands for RLI.")
@click.pass_context
def cli(cts):
    # Click group for github commands
    pass


@cli.command(
    name="create-repo",
    context_settings=CONTEXT_SETTINGS,
    help="Creates a repo with the given information",
)
@click.option("--repo-name", default=None)
@click.option("--repo-description", default=None)
@click.option("--private", default="false")
@click.pass_context
def create_repo(ctx, repo_name, repo_description, private):
    repo = RLIGithub(get_rli_config_or_exit().github_config).create_repo(
        repo_name, repo_description, private
    )

    if repo:
        logging.info(f"Here is your new repo:\n{str(repo)}")
        sys.exit(ExitCode.OK)
    else:
        sys.exit(ExitCode.GITHUB_ERROR)
