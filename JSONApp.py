import logging
import fnmatch
from time import strftime
from os import path, getcwd, remove, makedirs, listdir
from shutil import copy
from json import load, dump
from json_templates_for_gsuite import CreateJsonTemplates
from ADUService import create_directory_service
from LDAPOperations import ADOperation
from global_vars import ADUConfigs

if __name__ == '__main__':
    if not path.exists(path.join(getcwd(), 'Logs')):
        makedirs(path.join(getcwd(), 'Logs'))
        
    logging.basicConfig(format = u'[%(asctime)s] %(levelname)s %(message)s', \
            level = logging.INFO, \
            handlers=[logging.FileHandler(path.join(getcwd(), 'Logs', \
            'aduoperations_' + strftime('%d-%m-%Y') + '.log'), 'a', 'utf-8')])

    logging.getLogger('googleapiclient').setLevel(logging.ERROR)
    logging.getLogger('oauth2client').setLevel(logging.ERROR)

    if not path.exists(path.join(getcwd(), 'Back_up')):
        makedirs(path.join(getcwd(), 'Back_up'))

    if not path.exists(path.join(getcwd(), 'Import')):
        makedirs(path.join(getcwd(), 'Import'))

    try:
        service_ldap = ADOperation(ADUConfigs['dc_ou'])
    except Exception as Error:
        logging.error(Error)
    else:
        if path.exists(path.join(getcwd(), 'Import', 'st_output.dat')):
            service_ldap.st_load()
        else:
            pass

    try:
        service = create_directory_service(ADUConfigs['credential_delegation'])
        service_transfer = create_directory_service(ADUConfigs['credential_delegation'], 'datatransfer')
    except Exception as Error:
        logging.error(Error)
    else:
        listOfGroups = list()
        groups = service.groups().list(customer='my_customer', \
        maxResults=500).execute()
        token = groups.get('nextPageToken', None)
        for group in groups['groups']:
            listOfGroups.append([group.get('name',''), \
            group.get('email','')])

        while token is not None:
            groups = service.groups().list(customer='my_customer', \
            pageToken=token, maxResults=500).execute()
            for group in groups['groups']:
                listOfGroups.append([group.get('name',''), \
                group.get('email','')])
            token = results.get('nextPageToken', None)

        operationStatus = str()
        jsonImportFile = dict()

        if len(fnmatch.filter(listdir(path.join(getcwd())), '*.json')) > 0:
            if not path.exists(path.join(getcwd(), 'Back_up', 'back_up_' + strftime('%d.%m.%Y'))):
                makedirs(path.join(getcwd(), 'Back_up', 'back_up_' + strftime('%d.%m.%Y')))
            for path_to_json in fnmatch.filter(listdir(path.join(getcwd())), '*.json'):
                copy(path_to_json, path.join(getcwd(), 'Back_up', 'back_up_' + strftime('%d.%m.%Y')))
        else:
            pass

        for argument in fnmatch.filter(listdir(path.join(getcwd())), '*.json'):
            with open(argument, "r", encoding='utf-8' ) as openedJsonFile:
                jsonImportFile = load(openedJsonFile)
                operationStatus = jsonImportFile["operation"]
                    
            if operationStatus == "add":

                if not path.exists(path.join(getcwd(), 'Export')):
                    makedirs(path.join(getcwd(), 'Export'))
                else:
                    if len(listdir(path.join(getcwd(), 'Export'))) > 0:
                        for file_in_dir in listdir(path.join(getcwd(), 'Export')):
                            remove(path.join(getcwd(), 'Export', file_in_dir))
                    else:
                        pass

                addUsersTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('addUsers')
                addGroupsTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('addGroups')
                ldapUsersTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('ldap')
                service_ldap.add(ldapUsersTemplates)

                for no in range(len(addUsersTemplates)):
                    try:
                        service.users().insert(body=addUsersTemplates[no]).execute()
                        logging.info(addUsersTemplates[no]["primaryEmail"] + " " + \
                                addUsersTemplates[no]["name"]["givenName"] + " " + \
                                addUsersTemplates[no]["name"]["familyName"] + \
                                " successfully added.")
                        with open(path.join(getcwd(), 'Export', "gsuit_email_" + \
                                            str(no + 1) + ".json"), 'w') as jsonExportFile:
                            dump({"email": addUsersTemplates[no]["primaryEmail"], \
                            "index": "{0}".format(no+1), \
                            "password": addUsersTemplates[no]["password"], \
                            "ldap_password": ldapUsersTemplates[no][4],}, jsonExportFile)
                    except Exception as Error:
                        logging.error(addUsersTemplates[no]["primaryEmail"] + " " + \
                                addUsersTemplates[no]["name"]["givenName"] + " " + \
                                addUsersTemplates[no]["name"]["familyName"] + \
                                " error while adding.")
                        logging.error(Error)
                        
                for template in addGroupsTemplates:
                    group_exist = False
                    for group in listOfGroups:
                        if group == template[0]:
                            try:
                                service.members().insert(groupKey=template[0], body=template[1]).execute()
                                logging.info(template[1]["email"] + " successfully added to group " + template[0])
                            except Exception as Error:
                                logging.error(Error)
                                logging.error(template[1]["email"] + " error while adding to group " + str(template[0]))
                            group_exist = True
                            break
                        else:
                            continue
                            
                    if group_exist == False:
                        group_body = {
                            "name": "{0}".format(template[0].split('.')[0]),
                            "email": "{0}".format(template[0])
                                }
                        try:
                            service.groups().insert(body=group_body).execute()
                            logging.info(template[1]["email"] + " successfully create group " + template[0].split('.')[0])
                        except Exception as Error:
                            logging.error(Error)
                            logging.error(template[1]["email"] + " error while creating group " + str(template[0].split('.')[0]))
                            
                        
                        try:
                            service.members().insert(groupKey=template[0], body=template[1]).execute()
                            logging.info(template[1]["email"] + " successfully added to group " + template[0])
                        except Exception as Error:
                            logging.error(Error)
                            logging.error(template[1]["email"] + " error while adding to group " + str(template[0]))
                            
                try:
                    service.members().insert(groupKey=template[0], body=template[1]).execute()
                    logging.info(template[1]["email"] + " successfully added to group " + template[0])
                except Exception as Error:
                    logging.error(Error)
                    logging.error(template[1]["email"] + " error while adding to group " + str(template[0]))
                                
                '''
                for item in addGroupsTemplates:
                    try:
                        service.members().insert(groupKey=item[0], body=item[1]).execute()
                        logging.info(item[1]["email"] + " successfully added to group " + item[0])
                    except Exception as Error:
                        logging.error(Error)
                        logging.error(item[1]["email"] + " error while adding to group " + str(item[0]))
                '''
                
                remove(argument)

            if operationStatus == "suspend":

                suspendUsersTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('suspendUsers')
                ldapUsersTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('ldap')
                service_ldap.suspend(ldapUsersTemplates)

                for item in suspendUsersTemplates:
                    try:
                        service.users().update(userKey=item[0], body=item[1]).execute()
                        logging.info(item[0] + " suspended")
                    except Exception as Error:
                        logging.error(item[0] + " suspend error")
                        logging.error(Error)

                remove(argument)

                disk_storage = service.users().get(userKey=ADUConfigs['back_up_account']).execute().get("id", None)
                suspended_users_list = list()
                results = service.users().list(customer="my_customer", \
                maxResults=500).execute()
                token = results.get('nextPageToken', None)
                users_list = results.get("users", [])
                for user in users_list:
                    if user.get("suspended", []) == True:
                        suspended_users_list.append(user)
                    else:
                        continue

                while token is not None:
                    results = service.users().list(customer="my_customer", \
                    pageToken=token, maxResults=500).execute()
                    users_list = results.get("users", [])
                    for user in users_list:
                        if user.get("suspended", []) == True:
                            suspended_users_list.append(user)
                        else:
                            continue
                    token = results.get('nextPageToken', None)

                target_list = list()
                if len(suspended_users_list) > 0:
                    for user in suspended_users_list:
                        target_list.append([user["id"], user["name"]["fullName"]])

                complete_transfers_list = list()
                users_to_delete = list()
                transfers_query_result = service_transfer.transfers().list().execute()
                data_transfers = transfers_query_result['dataTransfers']
                for transfers in data_transfers:
                    complete_transfers_list.append([transfers['oldOwnerUserId'], \
                    transfers['applicationDataTransfers']])

                for transfers in complete_transfers_list:
                    if len(transfers[1]) > 1:
                        for item in transfers[1]:
                            if item['applicationId'] == '55656082996' and \
                            item['applicationTransferStatus'] == 'completed':
                                users_to_delete.append(transfers[0])
                            else:
                                pass
                    else:
                        if transfers[1][0]['applicationId'] == '55656082996' and \
                        transfers[1][0]['applicationTransferStatus'] == 'completed':
                            users_to_delete.append(transfers[0])
                        else:
                            pass

                if len(target_list) > 0:
                    for user in target_list:
                        if user[0] not in users_to_delete:
                            transfer_template = {
                            "applicationDataTransfers": [ 
                                { 
                                "applicationTransferParams": [ 
                                    {
                                    "key": "PRIVACY_LEVEL", 
                                    "value": ["shared", "private"],
                                    },
                                ],
                                "applicationId": "55656082996", 
                                },
                            ],
                            "newOwnerUserId": "{0}".format(disk_storage), 
                            "oldOwnerUserId": "{0}".format(user[0]), 
                            }
                            try:
                                service_transfer.transfers().insert(body=transfer_template).execute()
                                logging.info(user[1] + " transfer Docs & Drive to service account successfully requested.")
                            except Exception as Error:
                                logging.error(user[1] + " error occured while transfer Docs & Drive to service account")
                                logging.error(Error)
                        else:
                            try:
                                service.users().delete(userKey=user[0]).execute()
                                logging.info(user[1] + " successfully deleted & license release.")
                            except Exception as Error:
                                logging.error(user[1] + " error occured while trying to delete.")
                                logging.error(Error)
                else:
                    pass
                    
            if operationStatus == "update":

                updateUsersTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('updateUsers')
                updateGroupsTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('addGroups')
                ldapUsersTemplates = CreateJsonTemplates(argument, \
                        listOfGroups, ADUConfigs['domen'], ADUConfigs['dc_ou']).get_data('ldap')
                service_ldap.update(ldapUsersTemplates)

                for item in updateUsersTemplates:
                    try:
                        service.users().update(userKey=item[0], body=item[1]).execute()
                        logging.info(item[0] + " " + "updated")
                    except Exception as Error:
                        logging.error(item[0] + " update error")
                        logging.error(Error)

                for item in updateGroupsTemplates:
                    try:
                        service.members().insert(groupKey=item[0], body=item[1]).execute()
                        logging.info(item[1]["email"] + " successfully added to group " + item[0])
                    except Exception as Error:
                        logging.error(item[1]["email"] + " error while adding to group " + str(item[0]))
                        logging.error(Error)

                remove(argument)
