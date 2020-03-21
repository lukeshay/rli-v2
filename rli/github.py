from base64 import b64encode
from github import Github, GithubException
from nacl import public, encoding
import logging
import requests


GITHUB_URL = "https://api.github.com"


class RLIGithub:
    def __init__(self, config):
        self.github = (
            Github(config.login, config.password)
            if config.password
            else Github(config.login)
        )
        self.config = config

    def create_repo(self, repo_name, repo_description="", private="false"):
        """Creates a Github repository for the user/org you specified in ~/.rli/config.json

        :param repo_name: The name of the repository
        :param repo_description: The description of the repository
        :param private: Whether or not the repo should be private. '"true"' or '"false"' are the options
        :return: None
        """

        logging.debug(f"Creating repo '{repo_name}'.")
        private = private == "true"

        try:
            return self.github.get_user().create_repo(
                repo_name,
                description=repo_description,
                private=private,
                auto_init=True,
            )
        except GithubException as e:
            if e.status == 422:
                logging.error("Repository name is taken.")
            else:
                logging.error("There was an exception when creating your repository.")

    def add_secrets(self, repo_name, secrets_to_add, secrets):
        """Adds the given secrets to the repository.

        :param repo_name: The repo to add the secrets to.
        :param secrets_to_add: The keys of the secrets to add
        :param secrets: Key value pairs of your secrets
        :return: None
        """

        logging.debug(f"Adding secrets to repo '{repo_name}'.")
        public_key = self.get_public_key(repo_name)
        public_key_key = public_key.get("key", None)
        public_key_id = public_key.get("key_id", None)

        if len(secrets_to_add) == 0:
            secrets_to_add = secrets.keys()

        for key in secrets_to_add:
            value = secrets[key]
            encrypted = self._encrypt_secret(public_key_key, value)

            response = self._put_encrypted_secret(
                repo_name, public_key_id, key, encrypted
            )

            if response.status_code != 204 and not response.ok:
                raise GithubException(response.status_code, response.json())

    def _put_encrypted_secret(self, repo, public_key_id, name, secret):
        return requests.put(
            url=f"{GITHUB_URL}/repos/{self.config.organization}/{repo}/actions/secrets/{name}",
            auth=(self.config.login, self.config.password),
            json={"encrypted_value": secret, "key_id": public_key_id},
        )

    def get_public_key(self, repo_name):
        """Gets the public key for the given repo.

        :raises GithubException
        :param repo_name: The repo to get the public key from
        :return: The key and key_id as a dict
        """

        response = requests.get(
            url=f"{GITHUB_URL}/repos/{self.config.organization}/{repo_name}/actions/secrets/public-key",
            auth=(self.config.login, self.config.password),
        )

        if response.ok:
            return response.json()

        raise GithubException(response.status_code, response.json())

    def _encrypt_secret(self, public_key, secret_value):
        """Encrypt a Unicode string using the public key."""
        public_key = public.PublicKey(
            public_key.encode("utf-8"), encoding.Base64Encoder()
        )
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return b64encode(encrypted).decode("utf-8")
