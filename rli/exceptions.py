class InvalidRLIConfiguration(Exception):
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        if self.message:
            return f"InvalidRLIConfiguration has been raised: {self.message}"
        else:
            return "InvalidRLIConfiguration has been raised."


class InvalidDeployConfiguration(Exception):
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        if self.message:
            return f"InvalidDeployConfiguration has been raised: {self.message}"
        else:
            return "InvalidDeployConfiguration has been raised."


class RLIDockerException(Exception):
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        if self.message:
            return f"RLIDockerException has been raised: {self.message}"
        else:
            return "RLIDockerException has been raised."
