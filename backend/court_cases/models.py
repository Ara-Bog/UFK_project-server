from django.db import models
from Auth_LDAP.models import CustomUser
from django.contrib.contenttypes.fields import GenericRelation

class CourtCases(models.Model):
    class Meta:
        verbose_name = 'Судебное дело'
        verbose_name_plural = 'Судебные дела'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Куратор', related_name='usercourt_as_user')
    name_court = models.CharField(blank=True, null=True, verbose_name='Наименование суда', max_length=255)
    plaintiff = models.CharField(verbose_name='Истец', max_length=500)
    defendant = models.CharField(verbose_name='Ответчик', max_length=500)
    co_defendant = models.CharField(blank=True, null=True,verbose_name='Соответчик', max_length=500)
    many_defendant = models.CharField(blank=True, null=True,verbose_name='Иные лица', max_length=500)
    category = models.CharField(verbose_name='Категория дела', max_length=255)
    claim = models.TextField(blank=True, null=True, verbose_name='Исковые требования')
    claim_summ = models.FloatField(verbose_name='Сумма исковых требований', default=0.0)
    number_case_in_first_instance = models.CharField(default="XXX", max_length=255, verbose_name='N дела в суде первой инстанции')
    number_case_in_numenklature = models.CharField(max_length=255, verbose_name='N дела по внутренней номенклатуре')
    archive = models.BooleanField(verbose_name='Архивное', default=False)
    is_checked = models.BooleanField(verbose_name='Дело проверено', default=False)
    is_loaded = models.BooleanField(verbose_name='Выгруженно из СКИАО', default=False)
    
    notify_tasks = GenericRelation('Auth_LDAP.NotifyTask', related_query_name="court")

    def __str__(self):
        return f'{self.number_case_in_first_instance} | {self.number_case_in_numenklature}' 

class TypesEventsCourtCases(models.Model):
    class Meta:
        verbose_name = 'Тип инстанции'
        verbose_name_plural = 'Типы инстанций'

    name = models.CharField(verbose_name='Судебная инстанция', max_length=255)

    def __str__(self):
        return f'{self.name}' 

class EventsCourtCases(models.Model):
    class Meta:
        verbose_name = 'Инстанция судебного дела'
        verbose_name_plural = 'Инстанции судебного дела'

    type_event = models.ForeignKey(TypesEventsCourtCases, on_delete=models.PROTECT, verbose_name='Тип инстанции')
    court_case = models.ForeignKey(CourtCases, related_name='events', on_delete=models.CASCADE, verbose_name='Судебное дело')

    dates_of_court_hearing = models.DateField(blank=True, null=True, verbose_name='Дата судебного заседания') 
    date_appel = models.DateField(blank=True, null=True, verbose_name='Дата подачи апелляционной/кассационной/надзорной жалобы') # во всех, кроме 1 инстанции
    date_appel_issue = models.DateField(blank=True, null=True, verbose_name='Дата вынесения апелляционного/кассационного/надзорного "определения/постановления"') # во всех, кроме 1 инстанции
    date_of_dicision = models.DateField(blank=True, null=True, verbose_name='Дата вынесения судебного акта') # только 1 инстанция (вынести в дел ??)
    date_of_dicision_force = models.DateField(blank=True, null=True, verbose_name='Дата вступления судебного акта в законную силу') # только 1 инстанция (вынести в дел ??)

    brief_operative_part = models.TextField(blank=True, verbose_name='Краткая резолютивная часть')
    date_of_receipt = models.DateField(blank=True, null=True, verbose_name='Дата поступления в Управление')

    need_appel = models.BooleanField(verbose_name='Необходимость подачи апелляционной/кассационной/надзорной жалобы', default=False)
    # Информация о направлении отчета в Минфин России 
    date_minfin = models.DateField(blank=True, null=True, verbose_name='Дата письма')
    number_letter_minfin = models.TextField(blank=True, null=True, verbose_name='Номер письма')

    
    def __str__(self) -> str:
        return f'{self.court_case} - {self.type_event}'
