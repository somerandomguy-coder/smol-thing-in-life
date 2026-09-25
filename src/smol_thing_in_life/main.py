import os
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage
from typing import List

import httpx
from dotenv import load_dotenv

load_dotenv()


class Mailer(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def send_message(self, from_addr: str, to_addr: List[str], subject, message):
        pass


class mailpit_mailer:
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port

    def send_message(self, from_addr: str, to_addr: List[str], subject, message):
        email = EmailMessage()
        email["From"] = from_addr
        email["To"] = ", ".join(to_addr)
        email["Subject"] = subject
        email.set_content(message)

        with smtplib.SMTP(self.ip, self.port) as server:
            err = server.send_message(email)
            if err:
                print(err)


subject = "Testing Testing"
message = "Hi, this is an automated message, please do not reply"
print(f"Sending message: {message} with subject: {subject} ")

resend_api = os.environ.get("KEY", None)


def send_message_mailpit():
    ip = os.environ.get("IP", "localhost")
    smtp_port = os.environ.get("SMTP_PORT", "1025")

    mailer = mailpit_mailer(ip=ip, port=smtp_port)

    from_email = "nobody@meomeo.hihi"
    to_email = ["nicholasle0205@gmail.com"]

    mailer.send_message(from_email, to_email, subject, message)

    print("Success sent message to mailpit")


def fetch_message_mailpit(limit: int):
    ip = os.environ.get("IP", "localhost")
    http_port = os.environ.get("http_PORT", "8025")

    url = f"http://{ip}:{http_port}/api/v1/messages"

    response = httpx.get(url, params={"limit": limit})
    response.raise_for_status()
    data = response.json()
    print(data)
    return data.get("messages", [])


data = fetch_message_mailpit(10)


for email in data:
    print(f"from: {email['From']['Address']}")
    print(f"Content: {email['Snippet']}")
    print("-" * 50)
