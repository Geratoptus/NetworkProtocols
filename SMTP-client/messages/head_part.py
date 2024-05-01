import base64
import os
import re
from typing import Optional

from messages.imessage_part import IMessagePart

RUSSIAN_SUBJECT_EXP = re.compile("[а-яА-ЯёЁ]")


class HeadMessagePart(IMessagePart):
    def __init__(self, boundary: str, receivers: list[str], subject: Optional[str] = None) -> None:
        self._boundary = boundary
        self._receivers = receivers
        self._subject = self._normalize_subject(subject)

        if len(self._receivers) == 0:
            raise ValueError("No receivers")

    @property
    def receivers(self) -> list[str]:
        return self._receivers

    @classmethod
    def _transform_mail(cls, receiver: str) -> str:
        return f"<{receiver}>"

    def build(self) -> str:
        message_part = [
            f"From: <{os.getenv('LOGIN')}@yandex.ru>\n",
            f"To: " + ",\n\t".join(map(self._transform_mail, self._receivers)) + "\n",
        ]

        if self._subject is not None:
            message_part.append(f"Subject: {self._subject}\n")

        message_part += [
            f"MIME-Version: 1.0\n",
            f"Content-Type: multipart/mixed;boundary=\"{self._boundary}\"\n\n\n",
        ]
        return "".join(message_part)

    @classmethod
    def _normalize_subject(cls, subject: str) -> str:
        if subject and not RUSSIAN_SUBJECT_EXP.search(subject):
            return subject

        parts = []
        for i in range(0, len(subject), 30):
            part = subject[i:min(len(subject), i + 30)]
            base64part = base64.b64encode(part.encode()).decode()
            parts.append(f'=?utf-8?B?{base64part}?=')
        return "\n\t".join(parts)
