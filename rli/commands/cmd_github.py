import click
import sys
import logging
from rli.cli import CONTEXT_SETTINGS
from rli.github import RLIGithub
from rli.config import get_rli_config_or_exit
from rli.constants import ExitCode
from rli.exceptions import InvalidRLIConfiguration
from github import GithubException


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


@cli.command(
    name="add-secrets",
    context_settings=CONTEXT_SETTINGS,
    help="Adds or updates specified secrets from ~/.rli/secrets.json to the given "
    "repo.",
)
@click.option(
    "--repo-name",
    default=None,
    help="The name of the repo where the secrets should be added or updated.",
)
@click.option(
    "--secret",
    "-s",
    multiple=True,
    help="The secret to be added to the repo. Multiple can be specified. If "
    "none are specified, all will be added.",
)
@click.pass_context
def add_secrets(ctx, repo_name, secret):
    if not repo_name:
        logging.error("You must provide a repo name!")
        sys.exit(ExitCode.MISSING_ARG)

    rli_config = get_rli_config_or_exit()

    try:
        RLIGithub(rli_config.github_config).add_secrets(
            repo_name, secret, rli_config.rli_secrets
        )
    except InvalidRLIConfiguration:
        logging.error("Your Github RLI configuration is incorrect.")
        sys.exit(ExitCode.INVALID_RLI_CONFIG)
    except GithubException:
        logging.error("There was an error while adding secrets.")
        sys.exit(ExitCode.GITHUB_ERROR)
    except Exception:
        logging.error("There was an unexpected error while adding secrets.")
        sys.exit(ExitCode.UNEXPECTED_ERROR)

    logging.info("Successfully added all secrets to your repo.")
    sys.exit(ExitCode.OK)
