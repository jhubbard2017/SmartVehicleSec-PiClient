# -*- coding: utf-8 -*-
#
# utility class managing panic response contacts and sending out alert emails
#

import os
import os.path
import yaml
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from securityclientpy import _logger


class PanicResponse(object):
    """handles panic response communication to selected contacts given by client

    With this module, we will be able to send text messages and emails to selected contacts
    when a bad alert is happening or when the panic button is pressed by someone in the vehicle
    """

    _MAIL_SERVER = 'smtp.gmail.com'
    _MAIL_PORT = 587
    _SYSTEM_EMAIL = 'smart.vehicle.sec@gmail.com'
    _SYSTEM_PASSWORD = 'seniordesign2017'
    _SYSTEM_EMAIL_SUBJECT = 'ALERT MESSAGE FROM [{0}]'

    def __init__(self):
        self.total_emails_sent = 0

    def send_message(self, email_address):
        """sends warning message (email) to contact with name

        returns:
            bool
        """
        success = True

        sent = self.construct_email_and_send(email_address)
        if not sent:
            _logger.debug('Error. Email could not be sent to [{0}]'.format(contact['email']))
            return not success

        return success


    def construct_email_and_send(self, email_addr):
        """constructs an HTML email and sends to specified recipient

        args:
            email: str

        returns:
            bool
        """
        success = True

        email = MIMEMultipart('alternative')
        email['Subject'] = PanicResponse._SYSTEM_EMAIL_SUBJECT.format(email)
        email['From'] = PanicResponse._SYSTEM_EMAIL
        email['To'] = email_addr

        # Create both plaintext and html version so that email application can render either when needed
        plaintext_version = "Plaintext version"
        html_version = "HTML version"
        plaintext = MIMEText(plaintext_version, 'plain')
        html = MIMEText(html_version, 'html')

        # Attach both plaintext and html to email
        email.attach(plaintext)
        email.attach(html)

        try:
            mail = smtplib.SMTP(PanicResponse._MAIL_SERVER, PanicResponse._MAIL_PORT)
            mail.ehlo()
            mail.starttls()
            mail.login(PanicResponse._SYSTEM_EMAIL, PanicResponse._SYSTEM_PASSWORD)
            mail.sendmail(email_addr, PanicResponse._SYSTEM_EMAIL, email.as_string())
            self.total_emails_sent += 1
        except smtplib.SMTPException as e:
            _logger.debug('Could not send email. [{0}]'.format(e))
            mail.quit()
            return not success

        mail.quit()
        return success
