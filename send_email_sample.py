# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# THIS IS THE MINIMUM NEEDED CODE TO SEND AN EMAIL
# RUN THIS CODE

message = Mail(
    from_email='iba@uiowa.edu',    # this email address must be in Sendgrid's sender list
    to_emails='bodhi.psyche@gmail.com',
    subject='Sample Email From Science Alliance Portal',
    html_content='<strong>This is an email from Science Alliance Portal</strong>')
try:
    # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg = SendGridAPIClient('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')
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)