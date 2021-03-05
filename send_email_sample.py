# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# THIS IS THE MINIMUM NEEDED CODE TO SEND AN EMAIL
# RUN THIS CODE TO VERIFY THE INTEGRATION WORKS CORRECTLY


message = Mail(
    from_email='nam-h-le@uiowa.edu', # this email address must be in Sendgrid's sender list OR it must have a whitelisted domain name
    to_emails='bodhi.psyche@gmail.com',
    subject='Sample Email From Science Alliance Portal',
    html_content='<strong>This is an email from Science Alliance Portal</strong>')
try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)