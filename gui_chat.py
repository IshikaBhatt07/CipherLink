import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

from cipher import encrypt_message, decrypt_message

HOST = "0.0.0.0"
DEFAULT_PORT = 5000


class CipherLinkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CipherLink - Encrypted TCP Chat")
        self.root.geometry("900x780")
        self.root.minsize(760, 600)
        self.root.configure(bg="#111827")

        self.events = queue.Queue()
        self.conn = None
        self.server_socket = None
        self.connected = False
        self.closing = False
        self.connection_started = False
        self.socket_lock = threading.Lock()

        self.setup_style()
        self.build_interface()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.root.after(100, self.process_events)

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#111827")
        style.configure(
            "TLabel",
            background="#111827",
            foreground="#E5E7EB",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold"),
            foreground="#60A5FA",
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=8,
        )
        style.configure("TCombobox", padding=5)

    def build_interface(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main, text="CipherLink", style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            main, text="TCP CHAT  |  CAESAR SUBSTITUTION CIPHER"
        ).pack(anchor="w", pady=(0, 18))

        settings = ttk.Frame(main)
        settings.pack(fill="x", pady=(0, 12))

        ttk.Label(settings, text="Mode").grid(
            row=0, column=0, sticky="w", padx=(0, 6)
        )
        self.role = tk.StringVar(value="Server")
        self.role_box = ttk.Combobox(
            settings,
            textvariable=self.role,
            values=["Server", "Client"],
            state="readonly",
            width=12,
        )
        self.role_box.grid(row=0, column=1, padx=(0, 14))
        self.role_box.bind("<<ComboboxSelected>>", self.on_role_change)

        ttk.Label(settings, text="Server IP").grid(
            row=0, column=2, sticky="w", padx=(0, 6)
        )
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.host_entry = ttk.Entry(
            settings, textvariable=self.host_var, width=16
        )
        self.host_entry.grid(row=0, column=3, padx=(0, 14))

        ttk.Label(settings, text="Port").grid(
            row=0, column=4, sticky="w", padx=(0, 6)
        )
        self.port_var = tk.StringVar(value=str(DEFAULT_PORT))
        self.port_entry = ttk.Entry(
            settings, textvariable=self.port_var, width=7
        )
        self.port_entry.grid(row=0, column=5)

        self.connect_button = ttk.Button(
            main, text="Start Server", command=self.start_connection
        )
        self.connect_button.pack(anchor="w", pady=(0, 10))

        self.status_var = tk.StringVar(value="Status: Not connected")
        self.status_label = tk.Label(
            main,
            textvariable=self.status_var,
            bg="#1F2937",
            fg="#FBBF24",
            font=("Segoe UI", 10),
            anchor="w",
            padx=12,
            pady=10,
        )
        self.status_label.pack(fill="x", pady=(0, 12))

        ttk.Label(main, text="Conversation").pack(
            anchor="w", pady=(0, 6)
        )
        self.chat = tk.Text(
            main,
            height=4,
            bg="#1F2937",
            fg="#F9FAFB",
            insertbackground="white",
            font=("Consolas", 10),
            wrap="word",
            state="disabled",
            relief="flat",
            padx=12,
            pady=12,
        )
        self.chat.pack(fill="both", expand=True)
        self.chat.tag_configure("outgoing", foreground="#93C5FD")
        self.chat.tag_configure("incoming", foreground="#86EFAC")
        self.chat.tag_configure("system", foreground="#FBBF24")

        ttk.Label(main, text="Message").pack(
            anchor="w", pady=(12, 5)
        )
        send_row = ttk.Frame(main)
        send_row.pack(fill="x")

        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(
            send_row,
            textvariable=self.message_var,
            font=("Segoe UI", 11),
            state="disabled",
        )
        self.message_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self.message_entry.bind(
            "<Return>", lambda event: self.send_message()
        )

        self.send_button = ttk.Button(
            send_row,
            text="Send",
            command=self.send_message,
            state="disabled",
        )
        self.send_button.pack(side="right")

        ttk.Label(main, text="Encrypted payload preview").pack(
            anchor="w", pady=(12, 5)
        )
        self.payload_var = tk.StringVar(
            value="Your encrypted message will appear here."
        )
        self.payload_label = tk.Label(
            main,
            textvariable=self.payload_var,
            bg="#0B1220",
            fg="#C4B5FD",
            font=("Consolas", 10),
            anchor="w",
            justify="left",
            padx=12,
            pady=10,
            wraplength=680,
        )
        self.payload_label.pack(fill="x")

        self.on_role_change()

    def on_role_change(self, event=None):
        if self.connection_started:
            return
        if self.role.get() == "Server":
            self.connect_button.configure(text="Start Server")
            self.host_entry.configure(state="disabled")
        else:
            self.connect_button.configure(text="Connect to Server")
            self.host_entry.configure(state="normal")

    def add_chat(self, text, tag="system"):
        self.chat.configure(state="normal")
        self.chat.insert("end", text + "\n", tag)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def start_connection(self):
        if self.connection_started:
            return

        try:
            port = int(self.port_var.get())
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Port",
                "Enter a port number between 1 and 65535.",
            )
            return

        mode = self.role.get()
        host = self.host_var.get().strip()
        if mode == "Client" and not host:
            messagebox.showerror(
                "Missing Server IP",
                "Enter the server computer's IP address.",
            )
            return

        self.connection_started = True
        self.connect_button.configure(state="disabled")
        self.role_box.configure(state="disabled")
        self.host_entry.configure(state="disabled")
        self.port_entry.configure(state="disabled")
        self.status_var.set("Status: Connecting...")
        self.add_chat(f"Starting in {mode} mode.")

        threading.Thread(
            target=self.network_worker,
            args=(mode, host, port),
            daemon=True,
        ).start()

    def network_worker(self, mode, host, port):
        conn = None
        try:
            if mode == "Server":
                listener = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM
                )
                listener.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self.server_socket = listener
                listener.bind((HOST, port))
                listener.listen(1)
                self.events.put((
                    "status", f"Waiting for a client on port {port}..."
                ))
                conn, address = listener.accept()
            else:
                conn = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM
                )
                conn.settimeout(10)
                conn.connect((host, port))
                conn.settimeout(None)
                address = (host, port)

            with self.socket_lock:
                self.conn = conn

            self.events.put((
                "connected", f"Connected to {address[0]}:{address[1]}"
            ))
            self.receive_messages(conn)

        except Exception as error:
            if not self.closing:
                self.events.put(("error", str(error)))
        finally:
            with self.socket_lock:
                if self.conn is conn:
                    self.conn = None
                self.connected = False

            if conn:
                try:
                    conn.close()
                except OSError:
                    pass

            if self.server_socket:
                try:
                    self.server_socket.close()
                except OSError:
                    pass
                self.server_socket = None

            if not self.closing:
                self.events.put(("disconnected", "Connection closed."))

    def receive_messages(self, conn):
        buffer = b""
        while not self.closing:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data
            while b"\n" in buffer:
                encrypted_bytes, buffer = buffer.split(b"\n", 1)
                encrypted_text = encrypted_bytes.decode("utf-8")
                plain_text = decrypt_message(encrypted_text)
                self.events.put((
                    "incoming", (plain_text, encrypted_text)
                ))

    def send_message(self):
        if not self.connected:
            self.add_chat("Not connected to a peer.", "system")
            return

        message = self.message_var.get()
        if not message.strip():
            return

        encrypted = encrypt_message(message)
        print("Original message:", message)
        print("Encrypted message sent:", encrypted)
        data = (encrypted + "\n").encode("utf-8")

        try:
            with self.socket_lock:
                conn = self.conn
            if conn is None:
                self.add_chat(
                    "Connection is no longer available.", "system"
                )
                return

            conn.sendall(data)
            self.add_chat(f"You: {message}", "outgoing")
            self.payload_var.set(
                f"Sent encrypted payload: {encrypted}"
            )
            self.message_var.set("")
        except OSError as error:
            self.add_chat(f"Send failed: {error}", "system")
            self.status_var.set("Status: Send failed")

    def process_events(self):
        if self.closing:
            return

        while True:
            try:
                event, data = self.events.get_nowait()
            except queue.Empty:
                break

            if event == "status":
                self.status_var.set(f"Status: {data}")
                self.status_label.configure(fg="#FBBF24")

            elif event == "connected":
                self.connected = True
                self.status_var.set(f"Status: {data}")
                self.status_label.configure(fg="#86EFAC")
                self.message_entry.configure(state="normal")
                self.send_button.configure(state="normal")
                self.message_entry.focus_set()
                self.add_chat(data, "system")

            elif event == "incoming":
                plain_text, encrypted_text = data
                self.add_chat(f"Peer: {plain_text}", "incoming")
                self.payload_var.set(
                    f"Received encrypted payload: {encrypted_text}"
                )

            elif event == "error":
                self.status_var.set(
                    f"Status: Connection error — {data}"
                )
                self.status_label.configure(fg="#FCA5A5")
                self.add_chat(f"Connection error: {data}", "system")

                if not self.connected:
                    self.connect_button.configure(state="normal")
                    self.role_box.configure(state="readonly")
                    self.port_entry.configure(state="normal")
                    self.connection_started = False
                    self.on_role_change()

            elif event == "disconnected":
                self.connected = False
                self.status_var.set(f"Status: {data}")
                self.status_label.configure(fg="#FCA5A5")
                self.message_entry.configure(state="disabled")
                self.send_button.configure(state="disabled")
                self.add_chat(data, "system")

        self.root.after(100, self.process_events)

    def close_app(self):
        self.closing = True

        with self.socket_lock:
            conn = self.conn
            self.conn = None

        if conn:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                conn.close()
            except OSError:
                pass

        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CipherLinkGUI(root)
    root.mainloop()