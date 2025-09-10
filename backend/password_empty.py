SECRET_KEY = 'XXX'

MAIN_DB = {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': 'localhost',
    'PORT': '5432',
    'NAME': 'XXX',
    'USER': 'XXX',
    'PASSWORD': 'XXX'
}

# LDAP
LDAP_LIST_ATTRS = ['sAMAccountName', 'Name', 'mail', 'department', 'title', 'ObjectGUID', 
                   'MemberOf', 'GivenName', 'userAccountControl', 'msDS-parentdistname', 'description'] # Поля получаемые при синхронизации или входа
LDAP_HOST = "ldap://0.0.0.0" # Хост подключения
LDAP_HOST_USER = "CN=Объект,OU=Группа,DC=Домен" # Пользователь, под кем осуществляется вход
LDAP_HOST_USER_PASSWORD = "XXX" # Пароль пользователя
LDAP_SEARCH_USER = "OU=Группа,DC=Домен" # Группа, где осуществляется поиск сотрудников для авторизации
LDAP_SEARCH_GROUP = "OU=Группа,DC=Домен" # Группа, где осуществляется поиск групп
LDAP_GROUP_ADMIN = "CN=Объект,OU=Группа,DC=Домен" # Админская группа
LDAP_GROUP_CHIEF = "CN=Объект,OU=Группа,DC=Домен" # Группа начальников отделов
LDAP_GROUP_CHIEF_TER = "CN=Объект,OU=Группа,DC=Домен" # Группа начальников тер. отделов
LDAP_EXCLUDE_GROUPS = ["CN=Объект,OU=Группа,DC=Домен"] # Группа, сотрудников которой брать не нужно
LDAP_FOLDER_USERS = "OU=Группа,DC=Домен" # Группа для поиска всех сотрудников управления
LDAP_FOLDER_DELETE_USER = "OU=Группа,DC=Домен" # Группа удаленных пользователей 
LDAP_OGGSK_GROUP = "CN=Объект,OU=Группа,DC=Домен" # Группа пользователей (физическая) для принадлежности к отделу кадров
LDAP_OU_GROUP = "CN=Объект,OU=Группа,DC=Домен" # Группа пользователей (физическая) для принадлежности к юридическому отделу
LDAP_RUK_GROUP = "CN=Объект,OU=Группа,DC=Домен" # Группа пользователей (физическая) для принадлежности к руководству

# Для закрытого контура
# EMAIL_HOST = '0.0.0.0'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = 'xxx@fsfk.local'

# для теста локально в интернете
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'XXX@mail.ru'
EMAIL_HOST_PASSWORD = 'XXX'  # необходим пароль не от почты, а специально сгенерированный для smtp


