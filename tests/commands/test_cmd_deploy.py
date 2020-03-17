from unittest import TestCase
from unittest.mock import Mock
from rli import cli
from tests.helper import make_test_context
from rli.config import DockerConfig, GithubConfig
from rli.commands import cmd_deploy
from rli.constants import ExitCode


class CmdDeployTest(TestCase):
    def setUp(self):
        self.commit = "master"
        self.registry = "some.registry.com/"
        self.login = "some_login"
        self.password = "some_password"

        self.docker_config = DockerConfig(
            {"registry": self.registry, "login": self.login, "password": self.password}
        )

        self.github_config = GithubConfig(
            {
                "organization": "some_org",
                "login": "some_login",
                "password": "some_password",
            }
        )

        self.mock_rli_config = Mock()
        self.mock_rli_config.docker_config = self.docker_config
        self.mock_rli_config.github_config = self.github_config
        cmd_deploy.get_rli_config_or_exit = self.mock_rli_config

        self.mock_logging_info = Mock()
        cmd_deploy.logging.info = self.mock_logging_info
        self.mock_logging_error = Mock()
        cmd_deploy.logging.error = self.mock_logging_error
        self.mock_logging_debug = Mock()
        cmd_deploy.logging.debug = self.mock_logging_debug

        self.mock_deploy_config = Mock()
        cmd_deploy.get_deploy_config_or_exit = self.mock_deploy_config

        self.mock_rli_deploy_run_deploy = Mock()
        self.mock_rli_deploy_run_deploy.return_value = 0
        cmd_deploy.RLIDeploy.run_deploy = self.mock_rli_deploy_run_deploy

        self.mock_rli_git_checkout = Mock()
        self.mock_rli_git_checkout.return_value = 0
        cmd_deploy.RLIGit.checkout = self.mock_rli_git_checkout

        self.mock_sys = Mock()
        self.mock_sys_exit = Mock()
        self.mock_sys_exit.side_effect = SystemExit
        self.mock_sys.exit = self.mock_sys_exit
        cmd_deploy.sys = self.mock_sys

    def config_returns(
        self, rli_deploy_run_deploy=None, mock_rli_git_checkout=0,
    ):
        self.mock_rli_deploy_run_deploy.return_value = rli_deploy_run_deploy
        self.mock_rli_git_checkout.return_value = mock_rli_git_checkout

    def test_successful_with_checkout(self):
        with make_test_context(["deploy", "--commit", self.commit]) as ctx:
            cli.cli.invoke(ctx)

            self.mock_logging_error.assert_not_called()
            # self.mock_logging_info.assert_called_with(
            #     f"Running deploy for commit: {self.commit}."
            # )
            self.mock_logging_info.assert_called_with("Deploy finished successfully.")
            self.mock_sys_exit.assert_not_called()
            self.mock_rli_deploy_run_deploy.assert_called_once_with(self.commit)
            self.mock_rli_git_checkout.assert_called_once()

    def test_successful_skip_checkout(self):
        with make_test_context(
            ["deploy", "--commit", self.commit, "--skip-checkout"]
        ) as ctx:
            cli.cli.invoke(ctx)

            self.mock_logging_error.assert_not_called()
            # self.mock_logging_info.assert_called_with(
            #     f"Running deploy for commit: {self.commit}. Skipping checkout."
            # )
            self.mock_logging_info.assert_called_with("Deploy finished successfully.")
            self.mock_sys_exit.assert_not_called()
            self.mock_rli_deploy_run_deploy.assert_called_once_with(self.commit)
            self.mock_rli_git_checkout.assert_not_called()

    def test_failed_checkout(self):
        self.config_returns(mock_rli_git_checkout=1)

        with make_test_context(["deploy", "--commit", self.commit]) as ctx:
            with self.assertRaises(SystemExit):
                cli.cli.invoke(ctx)

            self.mock_rli_git_checkout.assert_called_once_with(self.commit)
            self.mock_logging_error.assert_called_once_with(
                f"Could not checkout commit: {self.commit}"
            )
            self.mock_sys_exit.assert_called_once_with(ExitCode.GIT_ERROR)
            self.mock_rli_deploy_run_deploy.assert_not_called()

    def test_failed_deploy_returned_none(self):
        self.config_returns(rli_deploy_run_deploy=None)

        with make_test_context(["deploy", "--commit", self.commit]) as ctx:
            with self.assertRaises(SystemExit):
                cli.cli.invoke(ctx)

            self.mock_rli_git_checkout.assert_called_once_with(self.commit)
            self.mock_rli_deploy_run_deploy.assert_called_once_with(self.commit)
            self.mock_logging_error.assert_called_once_with(
                "Deploy did not finish successfully."
            )
            self.mock_sys_exit.assert_called_once_with(ExitCode.DEPLOY_FAILED)

    def test_failed_deploy_returned_non_zerp(self):
        self.config_returns(rli_deploy_run_deploy=1)

        with make_test_context(["deploy", "--commit", self.commit]) as ctx:
            with self.assertRaises(SystemExit):
                cli.cli.invoke(ctx)

            self.mock_rli_git_checkout.assert_called_once_with(self.commit)
            self.mock_rli_deploy_run_deploy.assert_called_once_with(self.commit)
            self.mock_logging_error.assert_called_once_with(
                "Deploy did not finish successfully."
            )
            self.mock_sys_exit.assert_called_once_with(ExitCode.DEPLOY_FAILED)
