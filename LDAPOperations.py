import logging
from time import strftime
from re import search
from LDAPService import create_ldap_service
from os import path, getcwd, remove, listdir
from ldap3 import SUBTREE, ALL_ATTRIBUTES
from global_vars import ADUConfigs, MessageText
from GMAILService import GmailService, create_email_content

class ADOperation(object):
    def __init__(self, dc_ou):
        self.__service = create_ldap_service()
        self.__dc_ou = dc_ou
        self.__dc = ','.join([x for x in self.__dc_ou.split(',') if 'dc' in x])

    def __del__(self):
        self.__service.unbind()

    def add(self, templates):
        self.__templates = templates
        for template in self.__templates:
            self.__service.search(self.__dc, '(description={0})'.format(template[2]['description']), \
            attributes=['objectSid'], search_scope=SUBTREE)
            if self.__service.response[0].get('attributes', None) is None:
                try:
                    self.__status = self.__service.add(template[0], template[1], template[2])
                    self.__service.extend.microsoft.modify_password(template[0], template[4])
                    self.__service.modify(template[0], {'userAccountControl': [('MODIFY_REPLACE', 512)]})
                    self.__service.modify(template[0], {'pwdLastSet': ('MODIFY_REPLACE', [0])})
                    for ad_group in ADUConfigs['default_groups'].split(';'):
                        self.__service.extend.microsoft.add_members_to_groups(template[0], ad_group)
                    if template[0].split(',')[1] == 'ou=Заблоковані':
                        self.__service.modify(template[0], {'userAccountControl': [('MODIFY_REPLACE', 2)]})
                    else:
                        pass
                except Exception as Error:
                    logging.error(Error)
                    MessageText['ldap']['add']['error'].append([Error])
                else:
                    if self.__status == True:
                        self.__service.search(self.__dc, '(description={0})'.format(template[2]['description']), \
                        attributes=['mail', 'userPrincipalName', 'displayName', 'userAccountControl', \
                        'distinguishedName', 'objectSid'], search_scope=SUBTREE)
                        if self.__service.response[0].get('attributes', None) is not None:
                            logging.info("LDAP user " + self.__service.response[0]['attributes']['distinguishedName'] + " successfully added.")
                            MessageText['ldap']['add']['info'].append([self.__service.response[0]['attributes']['distinguishedName'], self.__service.response[0]['attributes']['userPrincipalName'], template[4]])
                    else:
                        logging.error("LDAP " + template[2]['displayName'] + " something wrong, user not added. " + str(self.__service.result))
                        MessageText['ldap']['add']['error'].append(["LDAP " + template[2]['displayName'] + " something wrong, user not added."])
            else:
                logging.warning("LDAP user " + template[2]['displayName'] + " already exist.")
                MessageText['ldap']['add']['warning'].append(["LDAP user " + template[2]['displayName'] + " already exist."])
                
        if len(MessageText['ldap']['add']['info']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Добавлены пользователи в Active Directory ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/add/info'))
        else:
            pass
        if len(MessageText['ldap']['add']['warning']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Добавлены пользователи в Active Directory (WARNINGS) ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/add/warning'))
        else:
            pass
        if len(MessageText['ldap']['add']['error']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Добавлены пользователи в Active Directory (ERRORS) ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/add/error'))
        else:
            pass

    def update(self, templates):
        self.__templates = templates
        for template in self.__templates:
            self.__service.search(self.__dc, '(description={0})'.format(template[2]['description']),
            attributes=['mail', 'userPrincipalName', 'displayName', 'userAccountControl', 'distinguishedName', 'objectSid'], \
            search_scope=SUBTREE)
            
            if self.__service.response[0].get('attributes', None) is not None:

                distinguishedName = self.__service.response[0]['attributes']['distinguishedName']
                
                # Обновляем имя пользователя на новое
                cn_new = search(r'^[cC][nN]=\w+\W?\w+\W?\s{1}\w+\s{1}\w+', template[0])
                if cn_new is not None:
                    cn_new = cn_new.group(0)
                    try:
                        self.__service.modify(distinguishedName, {'givenName': [('MODIFY_REPLACE', template[2]['givenName'])]})
                        self.__service.modify(distinguishedName, {'sn': [('MODIFY_REPLACE', template[2]['sn'])]})
                        self.__service.modify(distinguishedName, {'displayName': [('MODIFY_REPLACE', template[2]['displayName'])]})
                        self.__status = self.__service.modify_dn(distinguishedName, cn_new)
                    except Exception as Error:
                        logging.error(Error)
                        MessageText['ldap']['update']['error'].append([Error])
                    else:
                        if self.__status == True:
                            logging.info(distinguishedName + " is changed to " + cn_new)
                            MessageText['ldap']['update']['info'].append([distinguishedName + " is changed to " + cn_new])
                        else:
                            logging.error(distinguishedName + " something wrong, user name not changed. " + str(self.__service.result))
                            MessageText['ldap']['update']['error'].append([distinguishedName + " something wrong, user name not changed."])

                # Обновляем организационную единицу пользователя
                self.__service.search(self.__dc, '(description={0})'.format(template[2]['description']),
                attributes=['mail', 'userPrincipalName', 'displayName', 'userAccountControl', 'distinguishedName', 'objectSid'], \
                search_scope=SUBTREE)

                distinguishedName = self.__service.response[0]['attributes']['distinguishedName']
                                
                cn = search(r'^[cC][nN]=\w+\W?\w+\W?\s{1}\w+\s{1}\w+', distinguishedName)
                if cn is not None:
                    cn = cn.group(0)
                    try:
                        self.__status = self.__service.modify_dn(distinguishedName, cn, new_superior=template[3])
                    except Exception as Error:
                        logging.error(Error)
                        MessageText['ldap']['update']['error'].append([Error])
                    else:
                        if self.__status == True:
                            logging.info("DN of " + distinguishedName + " is changed to " + template[3])
                            MessageText['ldap']['update']['info'].append(["DN of " + distinguishedName + " is changed to " + template[3]])
                            distinguishedName = str(cn) + ',' + str(template[3])
                        else:
                            logging.error(distinguishedName + " something wrong, user DN not changed. " + str(self.__service.result))
                            MessageText['ldap']['update']['error'].append([distinguishedName + " something wrong, user DN not changed."])

                # Обновляем отдел пользователя
                self.__service.search(self.__dc, '(description={0})'.format(template[2]['description']),
                attributes=['mail', 'userPrincipalName', 'displayName', 'userAccountControl', 'distinguishedName', 'objectSid'], \
                search_scope=SUBTREE)

                distinguishedName = self.__service.response[0]['attributes']['distinguishedName']
                
                try:
                    self.__status = self.__service.modify(distinguishedName, {'department': [('MODIFY_REPLACE', template[2]['department'])]})
                except Exception as Error:
                    logging.error(Error)
                    MessageText['ldap']['update']['error'].append([Error])
                else:
                    if self.__status == True:
                        logging.info("Department of " + distinguishedName + " is changed to " + template[2]['department'])
                        MessageText['ldap']['update']['info'].append(["Department of " + distinguishedName + " is changed to " + template[2]['department']])
                    else:
                        logging.error(distinguishedName + " something wrong, user department not changed. " + str(self.__service.result))
                        MessageText['ldap']['update']['error'].append([distinguishedName + " something wrong, user department not changed."])

                # Обновляем должность пользователя
                try:
                    self.__status = self.__service.modify(distinguishedName, {'title': [('MODIFY_REPLACE', template[2]['title'])]})
                except Exception as Error:
                    logging.error(Error)
                    MessageText['ldap']['update']['error'].append([Error])
                else:
                    if self.__status == True:
                        logging.info("Title of " + distinguishedName + " is changed to " + template[2]['title'])
                        MessageText['ldap']['update']['info'].append(["Title of " + distinguishedName + " is changed to " + template[2]['title']])
                    else:
                        logging.error(distinguishedName + " something wrong, user title not changed. " + str(self.__service.result))
                        MessageText['ldap']['update']['error'].append([distinguishedName + " something wrong, user title not changed."])
            else:
                logging.warning("User with " + template[2]['description'] + " not found.")
                MessageText['ldap']['update']['warning'].append(["User " + template[0] + " not found."])

        if len(MessageText['ldap']['update']['info']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Обновление информации о пользователях Active Directory ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/update/info'))
        else:
            pass
        if len(MessageText['ldap']['update']['warning']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Обновление информации о пользователях Active Directory (WARNINGS) ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/update/warning'))
        else:
            pass
        if len(MessageText['ldap']['update']['error']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Обновление информации о пользователях Active Directory (ERRORS) ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/update/error'))
        else:
            pass
                
    def suspend(self, templates):
        self.__templates = templates
        for template in self.__templates:
            self.__service.search(self.__dc, '(description={0})'.format(template[2]['description']),
            attributes=['mail', 'userPrincipalName', 'displayName', 'userAccountControl', 'distinguishedName', 'objectSid'], \
            search_scope=SUBTREE)
            
            if self.__service.response[0].get('attributes', None) is not None:
                try:
                    self.__status = self.__service.modify(template[0], {'userAccountControl': [('MODIFY_REPLACE', 2)]})
                except Exception as Error:
                    logging.error(Error)
                    MessageText['ldap']['suspend']['error'].append([Error])
                else:
                    if self.__status == True:
                        logging.info("User " + template[0] + " suspended.")
                        MessageText['ldap']['suspend']['info'].append(["User " + template[0] + " suspended."])
                    else:
                        logging.error(template[0] + " something wrong, user account not suspended. " + str(self.__service.result))
                        MessageText['ldap']['suspend']['error'].append([template[0] + " something wrong, user account not suspended."])
            else:
                logging.warning("User " + template[0] + " not found.")
                MessageText['ldap']['suspend']['warning'].append(["User " + template[0] + " not found."])

        if len(MessageText['ldap']['suspend']['info']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Заблокированые пользователи в Active Directory ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/suspend/info'))
        else:
            pass
            
        if len(MessageText['ldap']['suspend']['warning']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Заблокированые пользователи в Active Directory (WARNINGS) ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/suspend/warning'))
        else:
            pass
            
        if len(MessageText['ldap']['suspend']['error']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Заблокированые пользователи в Active Directory (ERRORS) ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/suspend/error'))
        else:
            pass

    def st_load(self):
        self.__st_1c = list()
        self.__st_roots = list()
        self.__load_list = list()

        if path.exists(path.join(getcwd(), 'st_structure.dat')):
            remove(path.join(getcwd(), 'st_structure.dat'))
        else:
            pass
        
        with open(path.join(getcwd(), 'Import', 'st_output.dat'), mode='r', encoding='utf-8') as st_o:
            for line in st_o:
                self.__st_1c.append(line.replace('\n','').split(';'))
                
        with open("st_structure.dat", 'w', encoding='utf-8') as st_s:
            while len(self.__st_1c) > 1:
                if self.__st_1c[0][1] < self.__st_1c[1][1]:
                    self.__st_roots.append(self.__st_1c[0][0])
                    st_s.write(';'.join(self.__st_roots) + '\n')
                elif self.__st_1c[0][1] == self.__st_1c[1][1]:
                    self.__st_roots.append(self.__st_1c[0][0])
                    st_s.write(';'.join(self.__st_roots) + '\n')
                    self.__st_roots = self.__st_roots[:-1]
                else:
                    self.__st_roots.append(self.__st_1c[0][0])
                    st_s.write(';'.join(self.__st_roots) + '\n')
                    self.__st_roots = \
                    self.__st_roots[:-((int(self.__st_1c[0][1])-int(self.__st_1c[1][1]))+1)]
            
                self.__st_1c = self.__st_1c[1:]
            else:
                self.__st_roots.append(self.__st_1c[0][0])
                st_s.write(';'.join(self.__st_roots) + '\n')
                self.__st_1c = self.__st_1c[1:]

        with open(path.join(getcwd(), "st_structure.dat"), mode='r', encoding='utf-8') as st_s:
            for line in st_s:
                self.__load_list.append(line.replace('\n','').split(';'))

        for line in self.__load_list:
            line.reverse()
            try:
                self.__status = self.__service.add(('{}'+ self.__dc_ou).format("".join(["ou="+str(x)+"," for x in line])), 'organizationalUnit')
            except Exception as Error:
                logging.error(Error)
                MessageText['ldap']['st_import']['error'].append(["Organizational unit " + ('{}' + self.__dc_ou).format("".join(["ou="+str(x)+"," for x in line])) + " something wrong, user account not added."])
            else:
                if self.__status == True:
                    MessageText['ldap']['st_import']['info'].append(["Organizational unit " + ('{}' + self.__dc_ou).format("".join(["ou="+str(x)+"," for x in line])) + " successfully added."])
                else:
                    MessageText['ldap']['st_import']['warning'].append(["Organizational unit " + ('{}' + self.__dc_ou).format("".join(["ou="+str(x)+"," for x in line])) + " already exist."])
            
        if len(listdir(path.join(getcwd(), 'Import'))) > 0:
            for file_in_dir in listdir(path.join(getcwd(), 'Import')):
                remove(path.join(getcwd(), 'Import', file_in_dir))
        else:
            pass

        if len(MessageText['ldap']['st_import']['info']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Добавлены организационные единицы в Active Directory ' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/st_import/info'))
        else:
            pass

        if len(MessageText['ldap']['st_import']['warning']) != 0:
            GmailService().send_message("me",'script.notification@varus.ua', ADUConfigs['mail_to'], \
            'Добавлены организационные единицы в Active Directory (WARNINGS)' + strftime('%d-%m-%Y'), \
            create_email_content(MessageText, 'ldap/st_import/warning'))
        else:
            pass
