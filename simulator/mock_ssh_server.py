"""A tiny fake network device that speaks SSH.

This is NOT a real network OS emulator — it's just enough of an interactive
shell to prove the end-to-end flow (LLM -> validate -> SSH -> device) works,
without needing real Cisco/Fortigate/Aruba/Juniper/Ruckus hardware to publish
a working demo. It accepts a password login, drops into a vendor-flavored
prompt, and gives plausible canned responses to "show" commands and a generic
acknowledgement to anything that looks like a config command.
"""

import argparse
import os
import socket
import sys
import threading

import paramiko

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from netcopilot.vendors import VENDOR_CHOICES, get_vendor  # noqa: E402

HOST_KEY = paramiko.RSAKey.generate(2048)

USERNAME = os.getenv("NETCOPILOT_USERNAME", "admin")
PASSWORD = os.getenv("NETCOPILOT_PASSWORD", "admin")

EXIT_COMMANDS = {"exit", "quit", "logout"}


class MockServerInterface(paramiko.ServerInterface):
    def __init__(self):
        self.shell_requested = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == USERNAME and password == PASSWORD:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_shell_request(self, channel):
        self.shell_requested.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True


def simulate_command(cmd: str, vendor_key: str) -> str:
    """Return canned, vendor-flavored output for common show/config commands."""
    lowered = cmd.lower().strip()
    if not lowered:
        return ""
    if lowered.startswith("show vlan") or lowered.startswith("get system"):
        return f"[simulado:{vendor_key}] VLAN table — (mock, apenas para demo)"
    if lowered.startswith("show interfaces") or lowered.startswith("show interface"):
        return f"[simulado:{vendor_key}] Interface status — (mock, apenas para demo)"
    if any(k in lowered for k in ("write mem", "commit", "save config")):
        return f"[simulado:{vendor_key}] Configuração persistida (mock)."
    # Generic config-looking command: echo an ack, like a real device would
    return f"[simulado:{vendor_key}] OK: '{cmd}' aplicado (mock)."


def handle_client(client_socket: socket.socket, vendor_key: str) -> None:
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(HOST_KEY)
    server = MockServerInterface()
    transport.start_server(server=server)

    channel = transport.accept(20)
    if channel is None:
        transport.close()
        return

    server.shell_requested.wait(10)
    profile = get_vendor(vendor_key)
    prompt = f"{profile.cli_prompt} "

    channel.send(f"\r\n*** {profile.display_name} — dispositivo simulado (Network Config Copilot) ***\r\n")
    channel.send(prompt)

    buffer = ""
    try:
        while True:
            data = channel.recv(1024)
            if not data:
                break
            text = data.decode("utf-8", errors="ignore")
            for ch in text:
                if ch in ("\r", "\n"):
                    channel.send("\r\n")
                    stripped = buffer.strip()
                    if stripped.lower() in EXIT_COMMANDS:
                        channel.send("Connection closed.\r\n")
                        channel.close()
                        transport.close()
                        return
                    output = simulate_command(stripped, vendor_key)
                    if output:
                        channel.send(output.replace("\n", "\r\n") + "\r\n")
                    buffer = ""
                    channel.send(prompt)
                elif ch in ("\x7f", "\x08"):  # backspace / delete
                    if buffer:
                        buffer = buffer[:-1]
                        channel.send("\b \b")
                else:
                    buffer += ch
                    channel.send(ch)
    finally:
        channel.close()
        transport.close()


def serve(host: str, port: int, vendor_key: str) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)
    print(f"Mock SSH device ({vendor_key}) ouvindo em {host}:{port}")
    print(f"Login: {USERNAME} / {PASSWORD}  (ajustável via NETCOPILOT_USERNAME/NETCOPILOT_PASSWORD)")
    try:
        while True:
            client_socket, addr = sock.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, vendor_key), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nEncerrando simulador.")
    finally:
        sock.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Simulador SSH de dispositivo de rede (para demo/testes).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2222)
    parser.add_argument("--vendor", choices=VENDOR_CHOICES, default="cisco_ios")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    serve(args.host, args.port, args.vendor)
