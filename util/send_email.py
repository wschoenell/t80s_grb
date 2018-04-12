#!/usr/bin/env python
# Based on Python documentation example: https://docs.python.org/2/library/email-examples.html

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_html_email(origin, dest, subject, message, smtp_server, use_tls=True, username=None, password=None):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = origin
    msg['To'] = dest

    # Record the MIME types of both parts - text/plain and text/message.
    part = MIMEText(message, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part)

    # Send the message via the SMTP server.
    s = smtplib.SMTP(smtp_server)
    if use_tls:
        s.starttls()
    if username is not None:
        s.login(username, password)

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(origin, dest, msg.as_string())
    s.quit()


if __name__ == '__main__':
    from VOEventLib import Vutil as VOEventTools
    from voevent2html import format_to_string

    example_file = 'examples/SWIFT_BAT_Lightcurve_632888-389.xml'
    payload = payload = ''.join(open(example_file).readlines())
    message = format_to_string(VOEventTools.parseString(payload))
    send_html_email('t80s-admin@astro.ufsc.br', 'william@iaa.es', 'send_email.py test', message, '192.168.20.100')
