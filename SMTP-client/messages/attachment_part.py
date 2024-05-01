import os
from typing import Optional

import magic
import base64
from messages.imessage_part import IMessagePart


class AttachmentMessagePart(IMessagePart):
    def __init__(self, boundary: str, attachments: Optional[list[str]] = None) -> None:
        self._boundary = boundary
        self._attachments = attachments or []

    def build(self) -> str:
        message_part = []
        for filename in self._attachments:
            if not os.path.isfile(f"mail/attachments/{filename}"):
                print(f"Error on file: {filename}")
                continue

            message_part.append(f"--{self._boundary}\n")
            message_part.append(f"Content-Disposition: attachment;\n")
            message_part.append(f"\tfilename=\"{filename}\"\n")

            mime_type = magic.from_file(f"mail/attachments/{filename}", mime=True)

            message_part.append("Content-Transfer-Encoding: base64\n")
            message_part.append(f"Content-Type: {mime_type};\n")
            message_part.append(f"\tname=\"{filename}\"\n\n")

            with open(f"mail/attachments/{filename}", "rb") as file:
                attach = base64.b64encode(file.read()).decode("utf-8")
                message_part.append(attach + '\n')
        return "".join(message_part)
