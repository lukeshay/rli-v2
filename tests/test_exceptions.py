import unittest
from rli.exceptions import InvalidRLIConfiguration


class ExceptionsTest(unittest.TestCase):
    def test_no_message(self):
        with self.assertRaises(InvalidRLIConfiguration) as context:
            raise InvalidRLIConfiguration()

        self.assertEqual("InvalidRLIConfiguration has been raised.", str(context.exception))

    def test_message(self):
        message = "This is the message."
        with self.assertRaises(InvalidRLIConfiguration) as context:
            raise InvalidRLIConfiguration(message)

        self.assertEqual(f"InvalidRLIConfiguration has been raised: {message}", str(context.exception))



