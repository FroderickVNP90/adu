from json_templates_for_gsuite import CreateJsonTemplates
#from ADUService import create_directory_service

if __name__ == '__main__':
    #service = create_directory_service('valerii.perepelytsia@varus.ua')
    addUsersTemplates = CreateJsonTemplates('add.json', [['Тестова група', 'test.group@varus.ua'],], \
    'varus.ua', \
    'ou=users,ou=office,dc=netomega,dc=corp,dc=local').get_data('addGroups')
    for i in addUsersTemplates:
        print(i)
