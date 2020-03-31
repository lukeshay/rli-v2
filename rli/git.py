from rli.utils import bash
import logging


class RLIGit:
    @staticmethod
    def checkout(commit_or_branch):
        logging.debug(f"Checking out: {commit_or_branch}")
        return bash.run_command(["git", "checkout", commit_or_branch]).returncode
