"""
AdmitGuard v2 — Email Service
SMTP sending + IMAP reply tracking for candidate communications.
Gracefully degrades if not configured.
"""

import os
import ssl
import email
import smtplib
import imaplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

# Config from .env
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "AdmitGuard Admissions")


def is_available():
    """Check if email service is configured."""
    return bool(EMAIL_ADDRESS and EMAIL_PASSWORD)


def send_email(to_email, subject, body, candidate_id=None):
    """
    Send an email via SMTP.
    Returns: {"success": bool, "message_id": str|None, "error": str|None}
    """
    if not is_available():
        return {"success": False, "message_id": None, "error": "Email not configured."}

    try:
        msg = MIMEMultipart()
        msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_ADDRESS}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["X-AdmitGuard-CandidateID"] = candidate_id or ""

        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        message_id = msg["Message-ID"] or ""
        logger.info(f"Email sent to {to_email}: {subject}")

        return {
            "success": True,
            "message_id": message_id,
            "error": None,
        }

    except smtplib.SMTPAuthenticationError:
        return {"success": False, "message_id": None, "error": "SMTP authentication failed. Check EMAIL_PASSWORD (use app password for Gmail)."}
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return {"success": False, "message_id": None, "error": str(e)}


def check_replies(since_hours=24):
    """
    Check IMAP inbox for replies to admission emails.
    Looks for emails with 'Re:' in subject and AdmitGuard references.

    Returns: list of {"from": str, "subject": str, "body": str, "date": str, "message_id": str}
    """
    if not is_available():
        return []

    replies = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("INBOX")

        # Search for recent emails (within last N hours)
        status, data = mail.search(None, "ALL")
        if status != "OK":
            mail.logout()
            return []

        email_ids = data[0].split()
        # Check last 50 emails max
        recent_ids = email_ids[-50:] if len(email_ids) > 50 else email_ids

        for eid in recent_ids:
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg.get("Subject", "")

            # Only interested in replies
            if not subject.lower().startswith("re:"):
                continue

            from_addr = msg.get("From", "")
            date_str = msg.get("Date", "")
            message_id = msg.get("Message-ID", "")

            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

            replies.append({
                "from": from_addr,
                "subject": subject,
                "body": body[:2000],  # Cap body length
                "date": date_str,
                "message_id": message_id,
            })

        mail.logout()
        logger.info(f"Found {len(replies)} replies in inbox.")

    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP error: {e}")
    except Exception as e:
        logger.error(f"Reply check failed: {e}")

    return replies
