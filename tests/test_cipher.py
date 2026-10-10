
import unittest

from cipher import encrypt_message, decrypt_message


class TestSubstitutionCipher(unittest.TestCase):

    def test_encrypt_message(self):
        self.assertEqual(encrypt_message("Hello World"), "Khoor Zruog")

    def test_decrypt_message(self):
        self.assertEqual(decrypt_message("Khoor Zruog"), "Hello World")

    def test_encrypt_then_decrypt(self):
        message = "CipherLink 123!"
        self.assertEqual(decrypt_message(encrypt_message(message)), message)

    def test_empty_message(self):
        self.assertEqual(encrypt_message(""), "")
        self.assertEqual(decrypt_message(""), "")

    def test_uppercase_and_lowercase(self):
        self.assertEqual(encrypt_message("Az"), "Dc")
        self.assertEqual(decrypt_message("Dc"), "Az")


if __name__ == "__main__":
    unittest.main()