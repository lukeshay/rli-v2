class InvalidRLIConfiguration(Exception):
    def __init__(self, *args):
        self.message = args[0] if args else None

    def __str__(self):
        if self.message:
            return f"InvalidRLIConfiguration has been raised: {self.message}"
        else:
            return "InvalidRLIConfiguration has been raised."
