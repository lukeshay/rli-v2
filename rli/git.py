from rli.utils.bash import Bash
import logging


class RLIGit:
    @staticmethod
    def checkout(commit_or_branch):
        logging.debug(f"Checking out: {commit_or_branch}")
        return Bash.run_command(["git", "checkout", commit_or_branch]).returncode
