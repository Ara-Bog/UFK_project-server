from django.core.management.base import BaseCommand
import ldap.controls
from ldap.controls.libldap import SimplePagedResultsControl
from Auth_LDAP.models import CustomUser, Jobs, Departments
from password import *
import ldap
import pymorphy2
import re
from backend.settings import AUTH_LDAP_USER_FLAGS_BY_GROUP

class Command(BaseCommand):
    help = 'Синхронизация данных пользователей с LDAP'
    __pattern = re.compile(r'[^а-яА-Я0-9]|(?<=\D)0+')

    def __inflect_field(self, morph, value, type_inflect, gender="masc"):
        values = value.split(' ')
        value_parse = [morph.parse(word)[0] for word in values]
       
        value_inflect = [word.inflect({gender, type_inflect}) for word in value_parse]
        return " ".join([item.word if item else values[indx] for indx, item in enumerate(value_inflect)]).capitalize()

    def __to_unique(self, word):
        return self.__pattern.sub('', word.lower())

    def handle(self, *args, **options):
        l = ldap.initialize(LDAP_HOST)
        morph = pymorphy2.MorphAnalyzer()
        l.simple_bind_s(LDAP_HOST_USER, LDAP_HOST_USER_PASSWORD)
        
        page_size = 50
        filter_search = f'(&(objectClass=user)(!(msDS-parentdistname:={LDAP_FOLDER_DELETE_USER}))(!(memberOf:=CN=4800 Все терр. отделы УФК по Московской области,OU=Группы рассылки Терр. отделов,OU=Groups,OU=4800,OU=FT,DC=fsfk,DC=local)))'
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        results = l.search_ext(base=LDAP_FOLDER_USERS, scope=ldap.SCOPE_SUBTREE, filterstr=filter_search, attrlist=LDAP_LIST_ATTRS, serverctrls=[req_ctrl])

        total_created = 0
        total_updates = 0
        total = 0
        pages = 0
        CustomUser.objects.all().update(isChecked=False)

        while True:
            pages += 1
            rtype, rdata, rmsgid, serverctrls = l.result3(results)
            
            for _, user_data in rdata:
                user_update = False
                try:
                    if not user_data.get('mail'):
                        continue
                    data = {
                        'ldap_id': ''.join([hex(b) for b in user_data['objectGUID'][0]]),
                        'username' : user_data['sAMAccountName'][0].decode('utf-8'),
                        'email' : user_data['mail'][0].decode('utf-8'),
                        'isChecked': True
                    }
                    job_str = user_data['title'][0].decode('utf-8') if user_data.get('title') else 'NoJob'
                    job_unique = self.__to_unique(job_str)
                    job_el = Jobs.objects.filter(unique=job_unique).first()
                    if not job_el:
                        job_el = Jobs.objects.create(name=job_str, unique=job_unique)
                    if not job_el.job_inflected:
                        job_inflected, *job_any = job_str.split(' ')
                        job_el.job_inflected = " ".join([self.__inflect_field(morph, job_inflected, 'datv'), *job_any])
                        job_el.save()

                    department_str =  user_data['department'][0].decode('utf-8') if user_data.get('department') else 'NoDep'
                    dep_unique = self.__to_unique(department_str)
                    dep_el = Departments.objects.filter(unique=dep_unique).first()
                    if not dep_el:
                        dep_el = Departments.objects.create(name=department_str, unique=dep_unique) 
                    if not dep_el.department_inflected:
                        dep_inflected, *dep_any = department_str.split(' ')
                        dep_el.department_inflected = " ".join([self.__inflect_field(morph, dep_inflected, 'gent'), *dep_any])
                        dep_el.save()

                    name_str = user_data['name'][0].decode('utf-8') if user_data.get('name') else 'NoName'
                    name_key = name_str.lower().replace(' ', '')


                    group_dns = user_data.get('memberOf', [])
                    groups = [group_dn.decode('utf-8') for group_dn in group_dns]
                    for flag, group_dn in AUTH_LDAP_USER_FLAGS_BY_GROUP.items():
                        if group_dn in groups:
                            data[flag] = True

                    user, user_create = CustomUser.objects.update_or_create(ldap_id=data['ldap_id'], defaults=data)
                    if user_create or user.name_key != name_key:
                        parsed_name = morph.parse(user_data['GivenName'][0].decode('utf-8') if user_data.get('GivenName') else 'Иван')[0]
                        user.name = name_str
                        user.name_key = name_key
                        user_update = True
                        user.name_inflected = self.__inflect_field(morph, name_str, 'datv', parsed_name.tag.gender).title()
                    
                    if user_create or user.job.unique != job_unique:
                        user_update = True
                        user.job = job_el
                    
                    if user_create or user.department.unique != dep_unique:
                        user_update = True
                        user.department = dep_el
                        
                    user.save()
                    total_updates += user_update - user_create
                    total_created += user_create
                    total += 1
                except Exception as e:
                    print(f"Ошибка с пользователем - {user_data['sAMAccountName']} LDAP:\n{e}")
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: 
                    req_ctrl.cookie = pctrls[0].cookie
                    results = l.search_ext(base=LDAP_FOLDER_USERS, scope=ldap.SCOPE_SUBTREE, filterstr=filter_search, attrlist=LDAP_LIST_ATTRS, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break
        out = 'Найдено пользователей - {}; добавлены - {}; изменены - {}'.format(total, total_created, total_updates)
        self.stdout.write(self.style.SUCCESS(out))
        return out
