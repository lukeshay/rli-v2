import unittest
from rli.exceptions import InvalidRLIConfiguration, InvalidDeployConfiguration, RLIDockerException


class ExceptionsTest(unittest.TestCase):
    def test_InvalidRLIConfiguration_no_message(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            raise InvalidRLIConfiguration()

        self.assertEqual("InvalidRLIConfiguration has been raised.", str(context.exception))

    def test_InvalidRLIConfiguration_message(self):
        message = "This is the message."
        with self.assertRaises(InvalidRLIConfiguration) as context:
            raise InvalidRLIConfiguration(message)

        self.assertEqual(f"InvalidRLIConfiguration has been raised: {message}", str(context.exception))

    def test_InvalidDeployConfiguration_no_message(self):
        with self.assertRaises(InvalidDeployConfiguration) as context:
            raise InvalidDeployConfiguration()

        self.assertEqual("InvalidDeployConfiguration has been raised.", str(context.exception))

    def test_InvalidDeployConfiguration_message(self):
        message = "This is the message."
        with self.assertRaises(InvalidDeployConfiguration) as context:
            raise InvalidDeployConfiguration(message)

        self.assertEqual(f"InvalidDeployConfiguration has been raised: {message}", str(context.exception))

    def test_RLIDockerException_no_message(self):
        with self.assertRaises(RLIDockerException) as context:
            raise RLIDockerException()

        self.assertEqual("RLIDockerException has been raised.", str(context.exception))

    def test_RLIDockerException_message(self):
        message = "This is the message."
        with self.assertRaises(RLIDockerException) as context:
            raise RLIDockerException(message)

        self.assertEqual(f"RLIDockerException has been raised: {message}", str(context.exception))



