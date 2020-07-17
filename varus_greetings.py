import base64
import os
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email import encoders
from ADUService import create_directory_service
from global_vars import ADUConfigs

class VarusGreetings(object):
    def __init__(self):
        self.__service = create_directory_service(ADUConfigs['credential_delegation'], 'GmailAPI')

    def send_message(self, user_id, sender, to, subject, message_text, filename):
        self.__message = MIMEMultipart()
        self.__message['to'] = to
        self.__message['from'] = sender
        self.__message['subject'] = subject
        self.__message.attach(MIMEText(message_text, 'plain'))

        with open(filename, 'rb') as fp:
            self.__pdf_file = MIMEApplication(fp.read(),_subtype="pdf")

        self.__pdf_file.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(filename)))
        encoders.encode_base64(self.__pdf_file)
        
        self.__message.attach(self.__pdf_file)
        self.__base64_message = {'raw': base64.urlsafe_b64encode(self.__message.as_string().encode('UTF-8')).decode('ascii')}
        self.__service.users().messages().send(userId=user_id, body=self.__base64_message).execute()
