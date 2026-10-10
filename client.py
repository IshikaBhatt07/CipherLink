
import socket
import threading

from cipher import encrypt_message, decrypt_message

DEFAULT_HOST = "127.0.0.1"
PORT = 5000


def receive_messages(sock, stop_event):
    """Receive encrypted messages and display their plaintext."""
    try:
        with sock.makefile("r", encoding="utf-8") as reader:
            for encrypted_message in reader:
                encrypted_message = encrypted_message.rstrip("\n")
                original_message = decrypt_message(encrypted_message)

                print(f"\nServer: {original_message}")
                print("You: ", end="", flush=True)

    except (ConnectionError, OSError, UnicodeError) as error:
        if not stop_event.is_set():
            print(f"\nReceiving error: {error}")

    finally:
        stop_event.set()
        print("\nServer disconnected or connection closed.")


def main():
    host = input(
        f"Enter server IP address [{DEFAULT_HOST}]: "
    ).strip() or DEFAULT_HOST

    stop_event = threading.Event()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((host, PORT))

            print(f"\nConnected to CipherLink server at {host}:{PORT}")
            print("Type /quit to exit the chat.\n")

            receiver = threading.Thread(
                target=receive_messages,
                args=(client, stop_event),
                daemon=True,
            )
            receiver.start()

            try:
                while not stop_event.is_set():
                    message = input("You: ")

                    if message.strip().lower() == "/quit":
                        break

                    encrypted_message = encrypt_message(message)
                    print(f"Encrypted and sent: {encrypted_message}")

                    client.sendall(
                        (encrypted_message + "\n").encode("utf-8")
                    )

            except (ConnectionError, OSError) as error:
                print(f"\nConnection error: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nClosing chat.")

            finally:
                stop_event.set()
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

    except ConnectionRefusedError:
        print(
            "Connection refused. Start server.py first and check the IP and port."
        )
    except socket.gaierror:
        print("Invalid or unresolvable server address.")
    except OSError as error:
        print(f"Network error: {error}")

    print("Client stopped.")


if __name__ == "__main__":
    main()