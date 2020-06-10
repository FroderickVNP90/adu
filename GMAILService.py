import base64
import logging
from time import strftime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ADUService import create_directory_service
from global_vars import ADUConfigs, MessageText

class GmailService(object):
    def __init__(self):
        self.__service = create_directory_service(ADUConfigs['credential_delegation'], 'GmailAPI')

    def send_message(self, user_id, sender, to, subject, message_text):
        self.__message = MIMEMultipart('alternative')
        self.__message['to'] = to
        self.__message['from'] = sender
        self.__message['subject'] = subject
        self.__html_mime = MIMEText(message_text, 'html')
        self.__message.attach(self.__html_mime)
        self.__base64_message = {'raw': base64.urlsafe_b64encode(self.__message.as_string().encode('UTF-8')).decode('ascii'), 'payload': {'mimeType': 'text/html'}}
        try:
            self.__service.users().messages().send(userId=user_id, body=self.__base64_message).execute()
        except Exception as Error:
            logging.error(Error)

def create_email_content(message_text, mode):
    html_message = str()
    if mode == 'ldap/add/info':
        content = str()
        for line in message_text['ldap']['add']['info']:
            content += '<tr>{0}</tr>\n'.format(''.join(['<td>'+x+'</td>\n' for x in line]))
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#00b7ff;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th colspan="3">Added to Active Directory</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/add/warning':
        content = str()
        for line in message_text['ldap']['add']['warning']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#f5f067;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Added to Active Directory (WARNINGS)</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/add/error':
        content = str()
        for line in message_text['ldap']['add']['error']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#ff5959;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Added to Active Directory (ERRORS)</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/update/info':
        content = str()
        for line in message_text['ldap']['update']['info']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#00b7ff;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory updated users</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/update/warning':
        content = str()
        for line in message_text['ldap']['update']['warning']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#f5f067;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory updated users (WARNINGS)</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/update/error':
        content = str()
        for line in message_text['ldap']['update']['error']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#ff5959;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory updated users (ERRORS)</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/suspend/info':
        content = str()
        for line in message_text['ldap']['suspend']['info']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#00b7ff;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory suspended users </th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/suspend/warning':
        content = str()
        for line in message_text['ldap']['suspend']['warning']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#f5f067;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory suspended users (WARNINGS)</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/suspend/error':
        content = str()
        for line in message_text['ldap']['suspend']['error']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#ff5959;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory suspended users (ERRORS)</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/st_import/info':
        content = str()
        for line in message_text['ldap']['st_import']['info']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#00b7ff;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory organization units</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/st_import/warning':
        content = str()
        for line in message_text['ldap']['st_import']['warning']:
            content += '<tr>{0}</tr>\n'.format(line[0])
        html_message = \
        '<!DOCTYPE html>\n' + \
        '<html>\n' + \
            '<head>\n' + \
                '<meta charset="utf-8">\n' + \
                '<title></title>\n' + \
                '<style>\n' + \
                'table {\n' + \
                    'width:100%;\n' + \
                    '}\n' + \
                'th {\n' + \
                    'padding:10px;\n' + \
                    'font-family:Arial;\n' + \
                    'color:#ffffff;\n' + \
                    'text-align:left;\n' + \
                    'background-color:#f5f067;\n' + \
                    '}\n' + \
                '</style>\n' + \
            '</head>\n' + \
        '<body>\n' + \
            '<table border="1">\n' + \
                '<tr>\n' + \
                    '<th>Active Directory suspended users (WARNINGS)</th>\n' + \
                '</tr>\n' + \
                content + \
            '</table>\n' + \
        '</body>\n' + \
        '</html>'
        return html_message
    elif mode == 'ldap/st_import/error':
        pass
    else:
        return None
