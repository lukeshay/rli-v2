import click
import sys
import logging
from rli.cli import CONTEXT_SETTINGS
from rli.github import RLIGithub
from rli.deploy import RLIDeploy
from rli.config import RLIConfig, DeployConfig


@click.command(
    "deploy",
    context_settings=CONTEXT_SETTINGS,
    help="Runs a deploy. You must be in the directory that has the "
    "deploy/deploy.json file.",
)
@click.option(
    "--commit",
    default="master",
    help="The git commit you want to deploy. Master is the default. This will "
    "attempt to checkout this commit for the current dir. If you are doing "
    "Docker deploy, this must match the tag of a docker image in your "
    "registry. The latest image will be pulled if master is specified.",
)
@click.option(
    "--skip-checkout",
    is_flag=True,
    help="If this flag is used, checkout will be skipped",
)
@click.pass_context
def cli(ctx, commit, skip_checkout):
    rli_config = RLIConfig()
    rli_deploy_config = DeployConfig()

    if not skip_checkout:
        RLIGithub(rli_config.github_config).checkout(commit)

    RLIDeploy(rli_config, rli_deploy_config).run_deploy(commit)
