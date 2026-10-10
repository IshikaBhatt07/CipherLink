# CipherLink

# CipherLink — TCP Encrypted Chat

## Overview

CipherLink is a Python-based chat application that allows two
systems to exchange messages over TCP. Messages are encrypted
before transmission using a Caesar substitution cipher and
decrypted by the receiving system.

## Features

- TCP client-server communication using Python sockets
- Caesar substitution encryption and decryption
- Two-way messaging
- Concurrent receiving using threading
- Configurable server IP address
- Automated tests for the cipher

## Technologies

- Python 3.11
- TCP/IP sockets
- Threading
- Git and GitHub

## Project Structure

```text
CipherLink/
├── cipher.py
├── server.py
├── client.py
├── tests/
│   └── test_cipher.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3.11 or compatible Python 3 version
- VS Code or another Python editor
- Two terminals for local testing
- Two computers on a network for a two-system demonstration

No third-party Python packages are required.

## How to Run

1. Open a terminal in the project directory.
2. Start the server:

   `python server.py`

3. Open a second terminal.
4. Start the client:

   `python client.py`

5. For local testing, press Enter to use `127.0.0.1`.
6. Enter messages in either terminal.
7. Type `/quit` to end the chat.

## Network Configuration

The server listens on TCP port 5000.

For communication across two computers, enter the server
computer's LAN IPv4 address in the client.

Both computers must be able to communicate over the network,
and the server's firewall must permit the connection.

## Encryption Example

Plaintext: `Hello World`

Ciphertext: `Khoor Zruog`

Decrypted message: `Hello World`

## Limitations

The Caesar cipher is a classical educational substitution
cipher. It is not secure for real confidential communication
and does not provide message authentication or integrity.

## Learning Objectives

- Understand TCP client-server communication
- Apply substitution-based encryption and decryption
- Use Python sockets and threads
- Understand the role of IP addresses and port numbers
- Test a networking application

## Author

Ishika Bhatt 
B.Tech Computer Science and Engineering 