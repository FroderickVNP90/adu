"""Class creates templates for passing to GOOGLE API"""
#-*- coding: utf-8 -*-

import string
import random
from json import load
from re import sub, findall, escape
from os import path, getcwd
from difflib import SequenceMatcher
from password_generator import PasswordGenerator
from Validator import EmailValidator

class CreateJsonTemplates(object):
    """Class creates templates for passing to GOOGLE API"""
    def __init__(self, argv, groups, cond_groups, dyn_groups, domen, dc_ou):
        self.__domen = domen
        self.__dc_ou = dc_ou
        self.__email_validator = EmailValidator()
        self.__json_file = argv
        self.__groups = groups
        self.__cond_groups = cond_groups
        self.__dyn_groups = dyn_groups
        self.__pg = PasswordGenerator()
        self.__chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        self.__data = list()
        self.__list_cond_groups = list()
        self.__list_dyn_groups = list()
        self.__parsed_names_list = list()
        self.__transliteration_names_list = list()
        self.__email_adresses_list = list()
        self.__consolidated_list = list()
        self.__list_templates_add_users = list()
        self.__list_templates_update_users = list()
        self.__list_templates_suspend_users = list()
        self.__list_templates_adding_groups = list()
        self.__list_templates_for_ldap = list()

        with open(self.__json_file, "r", encoding='utf-8') as temp_json_file:
            self.__json_temp = load(temp_json_file)
            self.__json_enum = len(self.__json_temp["name"])
            for index_num in range(self.__json_enum):
                self.__data.append(\
                [self.__json_temp["name"][index_num], \
                self.__json_temp["position"][index_num], \
                self.__json_temp["subdivision"][index_num], \
                self.__json_temp["parent1"][index_num], \
                self.__json_temp["parent2"][index_num], \
                self.__json_temp["email"][index_num], \
                self.__json_temp["inn"][index_num], \
                self.__json_temp["phone"][index_num]])
                
        with open(self.__cond_groups, "r", encoding='utf-8') as cond_groups:
            temp_list_cond_groups = list()
            for line in cond_groups:
                temp_list_cond_groups.append(("".join(line.split(";"))).replace('\n',''))
            for line in temp_list_cond_groups:
                self.__list_cond_groups.append([line.split(":")[0], \
                [sub(r'(^r\')|(\'$)', '', x) for x in line.split(":")[1].split(" , ")]])
                
        with open(self.__dyn_groups, "r", encoding='utf-8') as dyn_groups:
            temp_list_dyn_groups = list()
            for line in dyn_groups:
                temp_list_dyn_groups.append(("".join(line.split(";"))).replace('\n',''))
            for line in temp_list_dyn_groups:
                self.__list_dyn_groups.append([line.split(' , ')[:3], \
                str(line.split(' , ')[3]).split(' : ')])

        self.__parse_names()
        self.__names_transliteration()
        self.__create_email_adresses()
        self.__consolidate_data()
        self.__get_ad_folders()

    def __parse_names(self):
        for user_data in self.__data:
            self.__sub_user_data = sub(r'\(\s?\w+\W?\w+\s?\)', ' ', user_data[0])
            if len(self.__sub_user_data.split()) == 3:
                self.__parsed_names_list.append(\
                [item.capitalize() for item in self.__sub_user_data.split()])
            else:
                self.__sub_user_data += ' ND'
                self.__parsed_names_list.append(\
                [item.capitalize() for item in self.__sub_user_data.split()])
        for index_num, item_data in enumerate(self.__parsed_names_list):
            if "Nd" in item_data[2]:
                self.__parsed_names_list[index_num][2] = " "

    def __names_transliteration(self):
        self.__transliteration_name = str()
        self.__transliteration_alphabet = [['а', ('a',)], ['б', ('b',)], ['в', ('v',)], \
        ['г', ('h',)], ['ґ', ('g',)], ['д', ('d',)], ['е', ('e',)], ['є', ('ye', 'ie')], \
        ['ж', ('zh',)], ['з', ('z',)], ['и', ('y',)], ['і', ('i',)], ['ї', ('yi', 'i')], \
        ['й', ('y', 'i')], ['к', ('k',)], ['л', ('l',)], ['м', ('m',)], ['н', ('n',)], \
        ['о', ('o',)], ['п', ('p',)], ['р', ('r',)], ['с', ('s',)], ['т', ('t',)], ['у', ('u',)], \
        ['ф', ('f',)], ['х', ('kh',)], ['ц', ('ts',)], ['ч', ('ch',)], ['ш', ('sh',)], \
        ['щ', ('shch',)], ['ю', ('yu', 'iu')], ['я', ('ya', 'ia')]]

        for parsed_name in self.__parsed_names_list:
            for word in parsed_name:
                for index_num, char in enumerate(word):
                    if index_num == 0:
                        for letter in self.__transliteration_alphabet:
                            if char.lower() == letter[0]:
                                self.__transliteration_name += letter[1][0]
                    elif index_num != 0 and \
                    char.lower() in \
                    [letter[0] for letter in self.__transliteration_alphabet if len(letter[1]) > 1]:
                        for letter in self.__transliteration_alphabet:
                            if char == letter[0]:
                                self.__transliteration_name += letter[1][1]
                    else:
                        for letter in self.__transliteration_alphabet:
                            if char == letter[0]:
                                self.__transliteration_name += letter[1][0]
                self.__transliteration_name += ' '
            self.__transliteration_names_list.append(\
            self.__transliteration_name.rstrip().split(' '))
            self.__transliteration_name = ''
        for index_num, item_data in enumerate(self.__transliteration_names_list):
            if len(item_data) < 3:
                self.__transliteration_names_list[index_num].append(" ")

    def __create_email_adresses(self):
        for num,name in enumerate(self.__transliteration_names_list):
            for type_num in range(3):
                if type_num == 0:
                    if self.__email_validator.validation(\
                    name[1] + '.' + name[0] + '@' + self.__domen,self.__data[num][6]) == True \
                    and len(name[1] + '.' + name[0]) <= 20:
                        self.__email_adresses_list.append(name[1] + '.' + name[0] + '@' + self.__domen)
                        break
                    else:
                        continue
                elif type_num == 1:
                    if self.__email_validator.validation(\
                    name[1][0] + '.' + name[0] + '@' + self.__domen,self.__data[num][6]) == True:
                        self.__email_adresses_list.append(name[1][0] + '.' + name[0] + '@' + self.__domen)
                        break
                    else:
                        continue
                elif type_num == 2:
                    if self.__email_validator.validation(\
                    name[1][0] + '.' + name[2][0] + '.' + name[0] \
                    + '@' + self.__domen,self.__data[num][6]) == True:
                        self.__email_adresses_list.append(\
                        name[1][0] + '.' + name[2][0] + '.' + name[0] + '@' + self.__domen)
                        break
                    else:
                        self.__email_adresses_list.append('Error')
                        break

    def __consolidate_data(self):
        '''
        [[0-Имя,1-Фамилия,2-Мєйл,3-Должность,4-Департамент\Отдел\Управление,5-Мєйл из файла,
        6-ИНН, 7-Телефон],8-Группа,9-Отчество,10-Папка на сервере,11-Организационная единица,]
        '''
        for index_num, item_data in enumerate(self.__data):
            self.__consolidated_list.append(\
            [self.__parsed_names_list[index_num][1], \
            self.__parsed_names_list[index_num][0], \
            self.__email_adresses_list[index_num], \
            item_data[1], \
            item_data[4] + ' | ' + item_data[3] + ' | ' + item_data[2], \
            item_data[5], \
            item_data[6], \
            item_data[7]])
            
        #Определение пользователей в группы
        for index_num, item_data in enumerate(self.__consolidated_list):                    
            if len(item_data) == 8:
                item_data.append([])
                
            for group in self.__list_dyn_groups:
                for item in item_data[4].split(' | '):
                    for condition in group[1]:
                        if findall(condition, item) != [] and group[0][0] == 'sub':
                            item_data[8].append(sub(r'\{\d\}', \
                            findall(group[0][2], item)[0], condition))
                        elif findall(sub(r'(^r\')|(\'$)', '', condition), item_data[3]) != [] \
                        and findall(r'^\(\w\s?\W\s?\d+\)', item) != [] \
                        and group[0][0] == 'sub':
                            item_data[8].append(sub(r'\{\d\}', \
                            findall(sub(r'(^r\')|(\'$)', '', \
                            group[0][2]), item)[0], group[0][1]))
                        else:
                            pass
                
            for group in self.__list_cond_groups:
                for condition in group[1]:
                    for item in item_data[4].split(' | '):
                        if findall(condition, item) != []:
                            item_data[8].append(group[0])
                            break
                        else:
                            pass
                    if findall(condition, item_data[3]) != []:
                        item_data[8].append(group[0])
                        break
                    else:
                        pass
                        
                    if condition == 'default':
                        item_data[8].append(group[0])
                        break
                    else:
                        pass
                            
                        
        for index_num, item_data in enumerate(self.__consolidated_list):
            item_data.append(self.__parsed_names_list[index_num][2])

    def __get_ad_folders(self):
        self.__home_folders = dict()
        self.__ad_folders = list()

        with open(path.join(getcwd(), "st_structure.dat"), "r", encoding='utf-8') as f:
            for line in f:
                self.__ad_folders.append((" | ".join(line.split(";"))).replace('\n',''))

        with open(path.join(getcwd(), "ha_dict.dat"), "r", encoding='utf-8') as f:
            for line in f:
                (key, val) = line[:-1].split(':')
                self.__home_folders[key] = val

        for index_num,item_data in enumerate(self.__consolidated_list):
            for item in item_data[4].split(" | "):
                if self.__home_folders.get(item, None) is not None:
                    self.__consolidated_list[index_num].append(self.__home_folders[item])
                    break
                else:
                    pass

            if len(item_data) == 10:
                self.__consolidated_list[index_num].append("ВРЕМЕННЫЕ")

        for index_num,item_data in enumerate(self.__consolidated_list):
            for line in self.__ad_folders:
                if len(line.split(" | ")) == 3:
                    if SequenceMatcher(None, line, item_data[4]).ratio() > 0.95:
                        reverse_line = line.split(" | ")
                        reverse_line.reverse()
                        reverse_line = " | ".join(reverse_line)
                        self.__consolidated_list[index_num].append(reverse_line)
                        break
                    else:
                        pass
                else:
                    if SequenceMatcher(None, " | ".join(line.split(" | ")[-3:]), item_data[4]).ratio() > 0.95:
                        reverse_line = line.split(" | ")
                        reverse_line.reverse()
                        reverse_line = " | ".join(reverse_line)
                        self.__consolidated_list[index_num].append(reverse_line)
                        break
                    else:
                        pass
                    
            if len(item_data) == 11:
                self.__consolidated_list[index_num].append("")
                
    def show(self):
        return self.__consolidated_list

    def get_data(self, mode):
        """Class creates templates for passing to GOOGLE API"""
        if mode == 'addUsers':
            for item in self.__consolidated_list:
                if item[5] == "":
                    self.__list_templates_add_users.append({"orgUnitPath" : "/omega", \
                        "primaryEmail" : "{0}".format(item[2]),\
                        "password" : "{0}".format(self.__pg.shuffle_password(self.__chars,8)), \
                        "externalIds": [{"value": "{0}".format(item[6]), \
                        "type": "organization"}], \
                        "organizations" : [{"title" : "{0}".format(item[3]),\
                        "department" : "{0}".format(item[4]),}],\
                        "name" : {"givenName" : "{0}".format(item[0]),\
                        "familyName" : "{0}".format(item[1]),},\
                        "changePasswordAtNextLogin" : True,})
                else:
                    self.__list_templates_add_users.append({"orgUnitPath" : "/omega", \
                        "primaryEmail" : "{0}".format(item[5]),\
                        "password" : "{0}".format(self.__pg.shuffle_password(self.__chars,8)), \
                        "externalIds": [{"value": "{0}".format(item[6]), \
                        "type": "organization"}], \
                        "organizations" : [{"title" : "{0}".format(item[3]),\
                        "department" : "{0}".format(item[4]),}],\
                        "name" : {"givenName" : "{0}".format(item[0]),\
                        "familyName" : "{0}".format(item[1]),},\
                        "changePasswordAtNextLogin" : True,})
            return self.__list_templates_add_users

        elif mode == 'updateUsers':
            for item in self.__consolidated_list:
                self.__list_templates_update_users.append([item[5], {"name" : \
                        {"givenName" : "{0}".format(item[0]), \
                        "familyName" : "{0}".format(item[1]),}, \
                        "organizations" : \
                        [{"title" : "{0}".format(item[3]),\
                    "department" : "{0}".format(item[4]),}],}])
            return self.__list_templates_update_users

        elif mode == 'suspendUsers':
            for item in self.__consolidated_list:
                self.__list_templates_suspend_users.append([item[5], {"suspended" : True}])
            return self.__list_templates_suspend_users

        elif mode == 'addGroups':
            for item in self.__consolidated_list:
                if item[5] == "":
                    if item is not None:
                        self.__list_templates_adding_groups.append([item[8], \
                        {"role" : "MEMBER", "type" : "USER", "email" : "{0}".format(item[2])}])
                else:
                    if item is not None:
                        self.__list_templates_adding_groups.append([item[8], \
                        {"role" : "MEMBER", "type" : "USER", "email" : "{0}".format(item[5])}])
            return self.__list_templates_adding_groups
            
        elif mode == 'ldap':
            for index_num, item_data in enumerate(self.__consolidated_list):
                self.__list_templates_for_ldap.append(\
                [('cn={0},{1}').format(\
                (item_data[1] + " " + item_data[0] + " " + item_data[9]).rstrip(), \
                "".join(["ou="+str(x).replace(",", "\5C,")+"," for x in item_data[11].split(" | ")]) + self.__dc_ou \
                if item_data[11] != "" else "ou=Заблоковані," + ",".join(self.__dc_ou.split(',')[1:])), \
                'user',
                {'givenName': "{0}".format(item_data[0]),\
                'sn': "{0}".format(item_data[1]), \
                'displayName': "{0}".format(\
                (item_data[1] + " " + item_data[0] + " " + item_data[9]).rstrip()), \
                'userPrincipalName': "{0}".format(\
                "".join([x for x in item_data[2].split('@') if x not in self.__domen])), \
                'sAMAccountName': "{0}".format(\
                "".join([x for x in item_data[2].split('@') if x not in self.__domen])), \
                'profilePath': "{0}".format("\\\\netomega.corp.local\\services\\profiles\\" + \
                "".join([x for x in item_data[2].split('@') if x not in self.__domen])), \
                'scriptPath': "{0}".format("logon.bat"), \
                'company': 'ТОВ "Омега"', \
                'title': "{0}".format(item_data[3]), \
                'department': "{0}".format(item_data[4].split(" | ")[2][:64]), \
                'c': 'UA', \
                'l': 'Дніпро', \
                "mail": "{0}".format(item_data[2]), \
                "info": "{0}".format("CN=" + (item_data[0] + \
                " " + \
                item_data[9] + \
                " " + \
                item_data[1]).rstrip() + \
                "/OU=omega/O=rush"), \
                "description": "{0}".format(item_data[6]), \
                "mobile": "{0}".format(item_data[7])}, \
                ('{0}' + self.__dc_ou).format(\
                ("".join(["ou="+str(x)+"," for x in item_data[11].split(" | ")]) \
                if item_data[11] != "" else "")), \
                self.__pg.shuffle_password(self.__chars,8)])
            return self.__list_templates_for_ldap
        else:
            return None
