import click
import sys
import logging
from rli.cli import CONTEXT_SETTINGS
from rli.git import RLIGit
from rli.deploy import RLIDeploy
from rli.config import DeployConfig, get_rli_config_or_exit, get_deploy_config_or_exit
from rli.constants import ExitCode


@click.command(
    "deploy",
    context_settings=CONTEXT_SETTINGS,
    help="Runs a deploy. You must be in the directory that has the "
    "deploy/deploy.json file. This command will attempt to checkout the commit "
    "inputted unless you use the '--skip-checkout' flag. When running a docker "
    "deploy, the image with the tag corresponding to the commit you pass in is "
    "pulled. The image is then tagged with 'latest' so it will be then image "
    "ran by docker-compose. If the commit specified is 'master', it pulls the "
    "image with the 'latest' tag.",
)
@click.option(
    "--commit",
    default="master",
    help="The git commit you want to deploy. 'master' is the default.",
)
@click.option(
    "--skip-checkout",
    is_flag=True,
    help="If this flag is used, checkout will be skipped",
)
@click.pass_context
def cli(ctx, commit, skip_checkout):
    logging.info(
        f"Running deploy for commit {commit}.{' Skipping checkout.' if skip_checkout else ''}"
    )
    rli_config = get_rli_config_or_exit()
    rli_deploy_config = get_deploy_config_or_exit()

    if not skip_checkout:
        checkout = RLIGit.checkout(commit)

        if checkout != 0:
            logging.error(f"Could not checkout commit: {commit}")
            sys.exit(ExitCode.GIT_ERROR)

    deploy = RLIDeploy(rli_config, rli_deploy_config).run_deploy(commit)

    if deploy is None or deploy != 0:
        logging.error("Deploy did not finish successfully.")
        sys.exit(ExitCode.DEPLOY_FAILED)
    else:
        logging.info("Deploy finished successfully.")
