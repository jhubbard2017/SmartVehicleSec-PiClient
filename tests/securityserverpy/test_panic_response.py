import unittest
from mock import patch
import smtplib

from securityclientpy.panic_response import PanicResponse


class TestLogs(unittest.TestCase):
    """set of test for panic_response.PanicResponse"""

    def setUp(self):
        self.panic = PanicResponse(file_name='tests/data/testcontacts.yaml')
        self.panic.clear()

    def tearDown(self):
        self.panic.clear()
        self.panic.store()

    def test_contacts_file_error(self):
        panic = PanicResponse(file_name='file doesnt exist')
        self.assertFalse(panic.contacts_loaded)

        success = panic.store()
        self.assertFalse(success)

    def test_add_contact(self):
        self.panic.add_contact('Hello', 'World', 'foo')
        self.assertEqual(self.panic.contact_count(), 1)

        my_contact = self.panic.get_contact('Hello')
        self.assertEqual(my_contact['phone'], 'World')
        self.assertEqual(my_contact['email'], 'foo')

    def test_add_contact_already_exist(self):
        success1 = self.panic.add_contact('Hello', 'World', 'foo')
        success2 = self.panic.add_contact('Hello', 'newWorld', 'newfoo')
        self.assertTrue(success1)
        self.assertFalse(success2)
        self.assertEqual(self.panic.contact_count(), 1)

    def test_add_contact_limit(self):
        for x in range(15):
            self.panic.add_contact('name{0}'.format(x), 'phone', 'email')

        success = self.panic.add_contact('foo', 'bar', 'jsu')
        self.assertFalse(success)

    def test_remove_contact(self):
        self.panic.add_contact('foo', 'bar', 'jsu')
        self.assertEqual(self.panic.contact_count(), 1)
        success = self.panic.remove_contact('foo')
        self.assertTrue(success)
        self.assertEqual(self.panic.contact_count(), 0)

    def test_remove_contact_not_found(self):
        self.panic.add_contact('foo', 'bar', 'jsu')
        self.assertEqual(self.panic.contact_count(), 1)
        success = self.panic.remove_contact('not found')
        self.assertFalse(success)
        self.assertEqual(self.panic.contact_count(), 1)

    def test_modify_contact(self):
        self.panic.add_contact('foo', 'bar', 'jsu')
        curr_contact = self.panic.get_contact('foo')
        self.assertEqual(curr_contact['phone'], 'bar')
        self.assertEqual(curr_contact['email'], 'jsu')

        success = self.panic.modify_contact('foo', phone='newbar', email='newfoo')
        self.assertTrue(success)

        modified_contact = self.panic.get_contact('foo')
        self.assertEqual(modified_contact['phone'], 'newbar')
        self.assertEqual(modified_contact['email'], 'newfoo')

    def test_modify_contact_not_found(self):
        self.panic.add_contact('foo', 'bar', 'jsu')
        curr_contact = self.panic.get_contact('foo')
        self.assertEqual(curr_contact['phone'], 'bar')

        success = self.panic.modify_contact('not found', phone='newbar', email='newfoo')
        self.assertFalse(success)

    def test_get_contact_not_found(self):
        self.panic.add_contact('foo', 'bar', 'jsu')
        mycontact = self.panic.get_contact('not found')
        self.assertIsNone(mycontact)

    def test_store_contacts(self):
        """test store devices in yaml file"""
        panic1 = PanicResponse(file_name='tests/data/testcontacts.yaml')
        panic1.add_contact('foo1', 'bar1', 'jsu1')
        panic1.store()

        panic2 = PanicResponse(file_name='tests/data/testcontacts.yaml')
        contact1 = panic1.get_contact('foo1')
        contact2 = panic2.get_contact('foo1')

        self.assertEqual(contact1['phone'], contact2['phone'])
        self.assertEqual(contact1['email'], contact2['email'])
        panic2.clear()
        panic2.store()

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

    def test_send_message_name_not_exist(self):
        self.panic.add_contact('name1', 'phone', 'email')
        self.setup_smtp_mocking()
        success = self.panic.send_message('name2')
        self.assertFalse(success)
        self.assertEqual(self.panic.total_emails_sent, 0)
        self.teardown_smtp_mocking()

    def test_send_message_name_exist(self):
        self.panic.add_contact('name1', 'phone', 'email')
        self.setup_smtp_mocking()
        success = self.panic.send_message('name1')
        self.assertTrue(success)
        self.assertEqual(self.panic.total_emails_sent, 1)
        self.teardown_smtp_mocking()

    def test_send_message_smtp_exception(self):
        self.panic.add_contact('name1', 'phone', 'email')
        self.setup_smtp_mocking(throw_exception=True)
        success = self.panic.send_message('name1')
        self.assertFalse(success)
        self.assertEqual(self.panic.total_emails_sent, 0)
        self.teardown_smtp_mocking()

    def test_send_message_all(self):
        for x in range(15):
            self.panic.add_contact('name{0}'.format(x), 'phone', 'email')
        self.setup_smtp_mocking()
        self.panic.send_message_all()
        self.assertEqual(self.panic.total_emails_sent, 15)
        self.teardown_smtp_mocking()

    def test_send_message_all_failure(self):
        for x in range(15):
            self.panic.add_contact('name{0}'.format(x), 'phone', 'email')
        self.setup_smtp_mocking(throw_exception=True)
        self.panic.send_message_all()
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
