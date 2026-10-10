
SHIFT = 3


def encrypt_message(message: str) -> str:
    """Encrypt a message using a Caesar substitution cipher."""
    encrypted = []

    for char in message:
        if "A" <= char <= "Z":
            encrypted.append(chr((ord(char) - ord("A") + SHIFT) % 26 + ord("A")))
        elif "a" <= char <= "z":
            encrypted.append(chr((ord(char) - ord("a") + SHIFT) % 26 + ord("a")))
        else:
            encrypted.append(char)

    return "".join(encrypted)


def decrypt_message(message: str) -> str:
    """Decrypt a Caesar substitution cipher message."""
    decrypted = []

    for char in message:
        if "A" <= char <= "Z":
            decrypted.append(chr((ord(char) - ord("A") - SHIFT) % 26 + ord("A")))
        elif "a" <= char <= "z":
            decrypted.append(chr((ord(char) - ord("a") - SHIFT) % 26 + ord("a")))
        else:
            decrypted.append(char)

    return "".join(decrypted)


if __name__ == "__main__":
    original = input("Enter a message: ")
    encrypted = encrypt_message(original)
    decrypted = decrypt_message(encrypted)

    print("Original message :", original)
    print("Encrypted message:", encrypted)
    print("Decrypted message:", decrypted)