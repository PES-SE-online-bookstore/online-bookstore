import base64
from email import message_from_bytes
from unittest.mock import Mock, patch

import requests
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.test import SimpleTestCase, override_settings

from qa.catalog import requirement

from config.email_backends import (
    GmailAPIEmailBackend,
    GmailAPIEmailBackendError,
)


class GmailAPIEmailBackendTests(SimpleTestCase):
    """Unit tests with HTTP mocked: no live Google handshake or mailbox delivery.

    Live delivery evidence is the controlled-mailbox test recorded separately.
    """

    qa_level = "Unit"
    qa_requirements = ("BOOK-F-020",)

    @requirement("BOOK-F-020", "BOOK-SR-001")
    @override_settings(
        GMAIL_API_CLIENT_ID="client-id",
        GMAIL_API_CLIENT_SECRET="client-secret",
        GMAIL_API_REFRESH_TOKEN="refresh-token",
        EMAIL_API_TIMEOUT=7,
        DEFAULT_FROM_EMAIL="bookstore.sender@gmail.com",
    )
    @patch("config.email_backends.requests.Session")
    def test_sends_email_through_gmail_https_api(self, session_class):
        session = session_class.return_value
        token_response = Mock()
        token_response.json.return_value = {"access_token": "access-token"}
        send_response = Mock()
        session.post.side_effect = [token_response, send_response]

        backend = GmailAPIEmailBackend()
        message = EmailMessage(
            subject="Order update",
            body="Your order was confirmed.",
            from_email="bookstore.sender@gmail.com",
            to=["buyer@example.com"],
        )

        self.assertEqual(backend.send_messages([message]), 1)
        self.assertIs(session.verify, True)
        self.assertEqual(session.post.call_count, 2)

        token_call = session.post.call_args_list[0]
        self.assertEqual(
            token_call.args[0],
            "https://oauth2.googleapis.com/token",
        )
        self.assertEqual(token_call.kwargs["timeout"], 7)
        self.assertEqual(
            token_call.kwargs["data"]["grant_type"],
            "refresh_token",
        )

        send_call = session.post.call_args_list[1]
        self.assertEqual(
            send_call.args[0],
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        )
        self.assertEqual(
            send_call.kwargs["headers"]["Authorization"],
            "Bearer access-token",
        )
        self.assertEqual(send_call.kwargs["timeout"], 7)

        raw = send_call.kwargs["json"]["raw"]
        raw += "=" * (-len(raw) % 4)
        parsed_message = message_from_bytes(base64.urlsafe_b64decode(raw))
        self.assertEqual(parsed_message["Subject"], "Order update")
        self.assertEqual(parsed_message["To"], "buyer@example.com")
        self.assertIn(
            "Your order was confirmed.",
            parsed_message.get_payload(decode=True).decode(),
        )

    @override_settings(
        GMAIL_API_CLIENT_ID="",
        GMAIL_API_CLIENT_SECRET="",
        GMAIL_API_REFRESH_TOKEN="",
        EMAIL_API_TIMEOUT=10,
    )
    @patch("config.email_backends.requests.Session")
    def test_missing_oauth_credentials_raise_configuration_error(
        self,
        session_class,
    ):
        backend = GmailAPIEmailBackend()

        with self.assertRaises(ImproperlyConfigured):
            backend.send_messages([
                EmailMessage(
                    "Subject",
                    "Body",
                    "from@example.com",
                    ["to@example.com"],
                )
            ])

        session_class.return_value.post.assert_not_called()

    @override_settings(
        GMAIL_API_CLIENT_ID="client-id",
        GMAIL_API_CLIENT_SECRET="client-secret",
        GMAIL_API_REFRESH_TOKEN="refresh-token",
        EMAIL_API_TIMEOUT=10,
    )
    @patch("config.email_backends.requests.Session")
    def test_empty_message_list_does_not_make_api_requests(self, session_class):
        backend = GmailAPIEmailBackend()

        self.assertEqual(backend.send_messages([]), 0)
        session_class.return_value.post.assert_not_called()

    @override_settings(
        GMAIL_API_CLIENT_ID="client-id",
        GMAIL_API_CLIENT_SECRET="client-secret",
        GMAIL_API_REFRESH_TOKEN="refresh-token",
        EMAIL_API_TIMEOUT=10,
    )
    @patch("config.email_backends.requests.Session")
    def test_fail_silently_returns_zero_on_api_failure(self, session_class):
        session_class.return_value.post.side_effect = requests.ConnectionError(
            "network error"
        )
        backend = GmailAPIEmailBackend(fail_silently=True)

        self.assertEqual(
            backend.send_messages(
                [
                    EmailMessage(
                        "Subject",
                        "Body",
                        "from@example.com",
                        ["to@example.com"],
                    )
                ]
            ),
            0,
        )

    @override_settings(
        GMAIL_API_CLIENT_ID="client-id",
        GMAIL_API_CLIENT_SECRET="client-secret",
        GMAIL_API_REFRESH_TOKEN="refresh-token",
        EMAIL_API_TIMEOUT=10,
    )
    @patch("config.email_backends.requests.Session")
    def test_api_failures_raise_sanitized_backend_error(self, session_class):
        session_class.return_value.post.side_effect = requests.ConnectionError(
            "network error"
        )
        backend = GmailAPIEmailBackend()

        with self.assertRaisesRegex(
            GmailAPIEmailBackendError,
            "Could not obtain a Gmail API access token",
        ):
            backend.send_messages([
                EmailMessage(
                    "Subject",
                    "Body",
                    "from@example.com",
                    ["to@example.com"],
                )
            ])
