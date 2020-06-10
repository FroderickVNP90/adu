from os import path, getcwd
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_EMAIL = 'adumaster@aduoperations.iam.gserviceaccount.com'

SERVICE_ACCOUNT_PKCS12_FILE_PATH = path.join(getcwd(), 'Cert', 'aduoperations-760d6b9340c5.p12')

def create_directory_service(user_email, mode='DirectoryAPI'):

    if mode == 'DirectoryAPI':

        credentials = ServiceAccountCredentials.from_p12_keyfile(
            SERVICE_ACCOUNT_EMAIL,
            SERVICE_ACCOUNT_PKCS12_FILE_PATH,
            'notasecret',
            scopes=['https://www.googleapis.com/auth/admin.directory.user', \
                    'https://www.googleapis.com/auth/admin.directory.group', \
                    'https://www.googleapis.com/auth/admin.directory.group.member',])

        credentials = credentials.create_delegated(user_email)
        return build('admin', 'directory_v1', credentials=credentials)
    elif mode == 'GmailAPI':
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            SERVICE_ACCOUNT_EMAIL,
            SERVICE_ACCOUNT_PKCS12_FILE_PATH,
            'notasecret',
            scopes=['https://mail.google.com/',])

        credentials = credentials.create_delegated(user_email)
        return build('gmail', 'v1', credentials=credentials)
    else:
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            SERVICE_ACCOUNT_EMAIL,
            SERVICE_ACCOUNT_PKCS12_FILE_PATH,
            'notasecret',
            scopes=['https://www.googleapis.com/auth/admin.datatransfer'])

        credentials = credentials.create_delegated(user_email)
        return build('admin', 'datatransfer_v1', credentials=credentials)
