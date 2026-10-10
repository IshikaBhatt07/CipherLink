
import socket
import threading

from cipher import encrypt_message, decrypt_message

HOST = "0.0.0.0"
PORT = 5000


def receive_messages(conn, stop_event):
    """Receive encrypted messages and display their plaintext."""
    try:
        with conn.makefile("r", encoding="utf-8") as reader:
            for encrypted_message in reader:
                encrypted_message = encrypted_message.rstrip("\n")
                original_message = decrypt_message(encrypted_message)

                print(f"\nClient: {original_message}")
                print("You: ", end="", flush=True)

    except (ConnectionError, OSError, UnicodeError) as error:
        if not stop_event.is_set():
            print(f"\nReceiving error: {error}")

    finally:
        stop_event.set()
        print("\nClient disconnected or connection closed.")


def main():
    stop_event = threading.Event()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)

        print("CipherLink TCP Server")
        print(f"Listening on port {PORT}...")
        print("Waiting for a client to connect.")

        conn, address = server.accept()

        with conn:
            print(f"Connected to client: {address[0]}:{address[1]}")
            print("Type /quit to exit the chat.\n")

            receiver = threading.Thread(
                target=receive_messages,
                args=(conn, stop_event),
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

                    conn.sendall(
                        (encrypted_message + "\n").encode("utf-8")
                    )

            except (ConnectionError, OSError) as error:
                print(f"\nConnection error: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nClosing chat.")

            finally:
                stop_event.set()
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

        print("Server stopped.")


if __name__ == "__main__":
    main()