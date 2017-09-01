import unittest
from mock import patch
import smtplib

from securityclientpy.panic_response import PanicResponse


class TestLogs(unittest.TestCase):
    """set of test for panic_response.PanicResponse"""

    def setUp(self):
        self.panic = PanicResponse()

    def test_construct_email_and_send_success(self):
        self.setup_smtp_mocking()
        success = self.panic.construct_email_and_send('my email')
        self.assertTrue(success)
        self.assertEqual(self.panic.total_emails_sent, 1)
        self.teardown_smtp_mocking()

    def test_construct_email_and_send_failure(self):
        self.setup_smtp_mocking(throw_exception=True)
        success = self.panic.construct_email_and_send('my email')
        self.assertFalse(success)
        self.assertEqual(self.panic.total_emails_sent, 0)
        self.teardown_smtp_mocking()

    def test_send_message(self):
        self.setup_smtp_mocking()
        success = self.panic.send_message('name1')
        self.assertTrue(success)
        self.assertEqual(self.panic.total_emails_sent, 1)
        self.teardown_smtp_mocking()

    def test_send_message_smtp_exception(self):
        self.setup_smtp_mocking(throw_exception=True)
        success = self.panic.send_message('name1')
        self.assertFalse(success)
        self.assertEqual(self.panic.total_emails_sent, 0)
        self.teardown_smtp_mocking()

    def setup_smtp_mocking(self, throw_exception=False):
        """sets up patchers needed to mock neccessary methods in smtplib.SMTP

        args:
            throw_exception: bool (defaults to False)
        """
        self.patcher1 = patch.object(smtplib.SMTP, 'login', return_value="login successful")
        self.patcher2 = patch.object(smtplib.SMTP, 'starttls', return_value="TLS started")
        if not throw_exception:
            self.patcher3 = patch.object(smtplib.SMTP, 'sendmail', return_value="Mail sent")
        else:
            self.patcher3 = patch.object(smtplib.SMTP, 'sendmail', side_effect=smtplib.SMTPException())

        # Start the patchers
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()

    def teardown_smtp_mocking(self):
        """stops all of the patchers used to mock neccessary methods in smtplib.SMTP"""
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
