from os import path, getcwd

MessageText = {"ldap":{"add":{"info":[],"error":[],"warning":[]}, \
"update":{"info":[],"error":[],"warning":[]}, \
"suspend":{"info":[],"error":[],"warning":[]}, \
"st_import":{"info":[],"error":[],"warning":[]}}}

ADUConfigs = dict()
with open(path.join(getcwd(), 'config.dat'), mode='r', encoding='utf-8') as configs:
    for config in configs:
        ADUConfigs[config.replace('\n','').split(':')[0]] = config.replace('\n','').split(':')[1]
