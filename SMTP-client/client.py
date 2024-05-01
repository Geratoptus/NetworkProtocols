from __future__ import annotations

import os
import ssl
import base64
import socket

from messages.message import Message


class SMTPClient:
    def __init__(self) -> None:
        self._client = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self._context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        self._client = self._context.wrap_socket(self._client)
        self._client.connect((os.getenv("HOST_ADDRESS"), int(os.getenv("PORT"))))
        self._client.recv(1024)

    def _send_request(self, data: str) -> str:
        self._client.send((data + "\n").encode())
        return self._client.recv(1024).decode()

    def send_message(self, message: Message) -> str:
        self.check_sender()
        message_text = message.build()
        self.check_receivers(message.receivers)

        self._send_request("DATA")
        return self._send_request(message_text)

    def auth_client(self) -> SMTPClient:
        self._send_request(f"EHLO {os.getenv('LOGIN')}")

        base64login = base64.b64encode(os.getenv("LOGIN").encode())
        base64password = base64.b64encode(os.getenv("PASSWORD").encode())

        self._send_request("AUTH LOGIN")
        self._send_request(base64login.decode())
        response = self._send_request(base64password.decode())

        if not response.startswith("235"):
            raise ConnectionError

        return self

    def check_receivers(self, receivers: list[str]) -> SMTPClient:
        for receiver in receivers:
            response = self._send_request(f"RCPT TO:{receiver}")
            if not response.startswith("250"):
                raise ValueError(receiver)

        return self

    def check_sender(self) -> SMTPClient:
        response = self._send_request(f"MAIL FROM:{os.getenv('LOGIN')}@yandex.ru")
        if not response.startswith("250"):
            raise ValueError(os.getenv('LOGIN'))

        return self
