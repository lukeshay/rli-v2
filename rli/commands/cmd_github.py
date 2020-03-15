import click
import logging
from rli.cli import CONTEXT_SETTINGS
from rli.github import RLIGithub
from rli.config import RLIConfig
from rli.exceptions import InvalidRLIConfiguration


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
@click.option('--repo-name', default=None)
@click.option('--repo-description', default=None)
@click.option("--private", default=False)
@click.pass_context
def create_repo(ctx, repo_name, repo_description, private):
    try:
        config = RLIConfig()
    except InvalidRLIConfiguration as e:
        logging.exception("Your ~/.rli/config.json file is invalid.", e)
        return
    except FileNotFoundError:
        logging.exception("Could not find ~/.rli/config.json")

    RLIGithub(config.github_config).create_repo(repo_name, repo_description, private)
