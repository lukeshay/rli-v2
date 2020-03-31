import subprocess
import logging
import os


def run_command(args, env=None) -> subprocess.CompletedProcess:
    """Runs the given command
    :param args: The arguments to pass in
    :param env: The env variables
    :return The completed process
    """

    logging.debug(f"Running the following command: {args}")

    new_env = os.environ

    if env:
        new_env.update(env)

    return subprocess.run(
        args=args, env=new_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )


def home_dir() -> str:
    return os.path.expanduser("~")
