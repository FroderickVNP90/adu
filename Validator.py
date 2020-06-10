from ADUService import create_directory_service
from LDAPService import create_ldap_service
from global_vars import ADUConfigs
from ldap3 import SUBTREE, ALL_ATTRIBUTES

class EmailValidator:
    def __init__(self):
        self.__service_directory = create_directory_service(ADUConfigs['credential_delegation'])
        self.__users_list = dict()
        self.__results = self.__service_directory.users().list(customer="my_customer", maxResults=500).execute()
        self.__token = self.__results.get('nextPageToken', None)
        for i in self.__results['users']:
            if i['orgUnitPath'] == '/omega':
                if i.get('externalIds', None) is not None:
                    self.__users_list[i['primaryEmail']] = i['externalIds'][0]['value']
                else:
                    self.__users_list[i['primaryEmail']] = None
            else:
                continue
        while self.__token is not None:
            self.__results = self.__service_directory.users().list(customer="my_customer", \
            pageToken=self.__token, maxResults=500).execute()
            for i in self.__results['users']:
                if i['orgUnitPath'] == '/omega':
                    if i.get('externalIds', None) is not None:
                        self.__users_list[i['primaryEmail']] = i['externalIds'][0]['value']
                    else:
                        self.__users_list[i['primaryEmail']] = None
                else:
                    continue
            self.__token = self.__results.get('nextPageToken', None)

    def validation(self,email,inn):
        if self.__users_list.get(email,None) is not None and self.__users_list.get(email,None) == inn:
            return True
        elif self.__users_list.get(email,None) is None:
            return True
        else:
            return False

class LDAPValidator:
    def __init__(self):
        pass
