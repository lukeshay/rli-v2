import subprocess
import logging
import os


class Bash:
    @staticmethod
    def run_command(args, env=None) -> subprocess.CompletedProcess:
        logging.debug(f"Running the following command: {args}")

        new_env = os.environ

        if env:
            new_env.update(env)

        return subprocess.run(
            args=args, env=new_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
