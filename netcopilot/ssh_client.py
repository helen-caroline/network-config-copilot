import time
from typing import Dict, List, Optional

import paramiko


class SwitchSSHClient:
    """Thin wrapper around an interactive Paramiko shell.

    Network device CLIs are stateful and prompt-driven (config mode, sub-modes,
    etc.), so this uses invoke_shell() rather than exec_command() — one command
    per exec_command() would lose the config-mode context between commands.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.timeout = timeout
        self._client: Optional[paramiko.SSHClient] = None
        self._shell = None

    def connect(self) -> None:
        self._client = paramiko.SSHClient()
        # AutoAddPolicy accepts unknown host keys without prompting — fine for a
        # local simulator or a lab device, NOT for a production network. A real
        # deployment should pin known_hosts and use RejectPolicy instead.
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename,
            timeout=self.timeout,
            allow_agent=False,
            look_for_keys=False,
        )
        self._shell = self._client.invoke_shell()
        self._drain()  # swallow the device's login banner/first prompt

    def _drain(self, wait: float = 0.4) -> str:
        time.sleep(wait)
        output = ""
        while self._shell.recv_ready():
            output += self._shell.recv(4096).decode("utf-8", errors="ignore")
        return output

    def run_commands(self, commands: List[str]) -> List[Dict[str, str]]:
        if self._shell is None:
            raise RuntimeError("connect() must be called before run_commands()")
        transcript = []
        for cmd in commands:
            self._shell.send(cmd + "\n")
            output = self._drain()
            transcript.append({"command": cmd, "output": output})
        return transcript

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
