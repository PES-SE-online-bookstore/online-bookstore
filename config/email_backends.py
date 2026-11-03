"""Django email backend for sending mail through the Gmail HTTPS API."""

import base64

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend


class GmailAPIEmailBackendError(Exception):
    """Raised when Gmail API authentication or delivery fails."""


class GmailAPIEmailBackend(BaseEmailBackend):
    """Send Django email messages using Gmail's HTTPS API.

    Uses an OAuth refresh token (not a Gmail password or App Password).
    ``requests`` certificate verification remains enabled for both OAuth and
    Gmail API requests.
    """

    token_url = "https://oauth2.googleapis.com/token"
    send_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.timeout = settings.EMAIL_API_TIMEOUT
        self.session = requests.Session()
        self.session.verify = True

    def close(self):
        self.session.close()

    def _credentials(self):
        credentials = {
            "client_id": settings.GMAIL_API_CLIENT_ID,
            "client_secret": settings.GMAIL_API_CLIENT_SECRET,
            "refresh_token": settings.GMAIL_API_REFRESH_TOKEN,
        }

        if not all(credentials.values()):
            raise ImproperlyConfigured(
                "Gmail API email requires GMAIL_API_CLIENT_ID, "
                "GMAIL_API_CLIENT_SECRET, and GMAIL_API_REFRESH_TOKEN."
            )

        return credentials

    def _access_token(self):
        credentials = self._credentials()

        try:
            response = self.session.post(
                self.token_url,
                data={
                    **credentials,
                    "grant_type": "refresh_token",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            token = response.json().get("access_token")
        except (requests.RequestException, ValueError, AttributeError) as exc:
            raise GmailAPIEmailBackendError(
                "Could not obtain a Gmail API access token."
            ) from exc

        if not token:
            raise GmailAPIEmailBackendError(
                "Google's token response did not include an access token."
            )

        return token

    @staticmethod
    def _encode_message(email_message):
        mime_message = email_message.message()
        raw_message = mime_message.as_bytes()
        return base64.urlsafe_b64encode(raw_message).decode("ascii").rstrip("=")

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0

        try:
            access_token = self._access_token()

            for email_message in email_messages:
                response = self.session.post(
                    self.send_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json={"raw": self._encode_message(email_message)},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                sent_count += 1

        except Exception as exc:
            if self.fail_silently:
                return sent_count
            if isinstance(exc, (GmailAPIEmailBackendError, ImproperlyConfigured)):
                raise
            raise GmailAPIEmailBackendError(
                "Gmail API email delivery failed."
            ) from exc

        return sent_count
