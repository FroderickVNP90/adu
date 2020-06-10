from ldap3 import Server, Connection, ALL
from os import path, getcwd
from global_vars import ADUConfigs

SERVER = ADUConfigs['ldap_server']
USER = ADUConfigs['ldap_user']
PASSWORD = ADUConfigs['ldap_password']

def create_ldap_service():
    return Connection(\
    Server(SERVER, get_info=ALL, use_ssl=True), \
    USER, \
    PASSWORD, \
    auto_bind=True)
