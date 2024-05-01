import json
from typing import Any

from dotenv import load_dotenv

from client import SMTPClient
from messages.message import MessageBuilder


if __name__ == '__main__':
    load_dotenv()

    with open("mail/mail.json", "r", encoding="utf-8") as file:
        
        mail_data: dict[str, Any] = json.load(file)
        message = (MessageBuilder.builder()
                   .set_subject(mail_data.get("subject"))
                   .set_body(mail_data.get("body"))
                   .add_receivers(*mail_data.get("receivers"))
                   .add_attachments(*mail_data.get("attachments")))

        SMTPClient().auth_client().send_message(message.build_message())
