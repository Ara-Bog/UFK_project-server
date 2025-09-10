from datetime import datetime, timedelta
from .models import EventsCourtCases, CustomUser
from datetime import timedelta
from Auth_LDAP.models import NotifyTask, TypesNotify

SCHEMA = {
    'first': {
        'message':  'Проверить факт вступления судебного акта в законную силу, либо заполнить дату подачи апелляционной жалобы',
        'term': [60, 45],
        'period': [10, 5]
    },
    'minfin': {
        'message':  'Отправить информацию в Минфин России до {}',
        'term': [30, 30, 30, 30, 30],
        'period': [5, 5, 5, 5, 5]
    },
    'appel': {
        'message':  [
            "Необходимо подать апелляционную жалобу до {}", 
            "Необходимо подать кассационную жалобу до {}",
            "Необходимо подать жалобу во 2-ую кассацию до {}",
            "Необходимо подать надзорную жалобу до {}",
        ],
        'term': [
            [30, 15],
            [90, 180],
            [90, 180],
            [90, 90],
        ],
        'period': [
            [5, 3],
            [15, 30],
            [15, 30],
            [15, 15],
        ]
    }
}

def create_task(event_id):
    event = EventsCourtCases.objects.get(id=event_id)
    court = event.court_case
    current_user = event.court_case.user
    now = datetime.now()

    court.notify_tasks.all().delete()
    if event.court_case.archive or not event.court_case.is_checked:
        return "Создание уведомлений не возможно"
    task = create_new_notify(court)

    is18Topic = event.court_case.category == '18-Глава УПК РФ'
    isFz = (event.court_case.category == '68-ФЗ') and (event.type_event.pk in range(2, 3))
    isCombine18AndFz = is18Topic or isFz
    indx = event.type_event.pk - 1

    date_for_calc = now
    select_date = event.date_appel_issue if event.date_appel_issue else event.date_of_dicision_force
    if event.need_appel:
        date_for_calc = event.date_appel_issue if event.date_appel_issue else event.date_of_dicision
        task.date_finish = date_for_calc + timedelta(days=SCHEMA['appel']['term'][indx][isCombine18AndFz])
        task.message = SCHEMA['appel']['message'][indx].format(task.date_finish.strftime("%d.%m.%Y"))
        task.period = SCHEMA['appel']['period'][indx][isCombine18AndFz]
        task.type_message = TypesNotify.objects.get(id=3)
        if event.date_appel_issue and event.type_event.id == 2:
            if not event.date_minfin and not event.number_letter_minfin:
                date_finish_added_task = select_date + timedelta(days=SCHEMA['minfin']['term'][indx])
                if date_finish_added_task:
                    added_task = create_new_notify(court)
                    added_task.type_message = TypesNotify.objects.get(id=2)
                    added_task.target = current_user
                    added_task.title = f"Уведомление по делу {event}"
                    added_task.message = SCHEMA['minfin']['message'].format(date_finish_added_task.strftime("%d.%m.%Y"))
                    added_task.period = SCHEMA['minfin']['period'][indx]
                    added_task.date_finish = date_finish_added_task
                    added_task.save()
                    dublicate_chiefs(added_task)
    elif select_date:
        if not event.date_minfin and not event.number_letter_minfin:
            task.date_finish = select_date + timedelta(days=30)
            task.message = SCHEMA['minfin']['message'].format(task.date_finish.strftime("%d.%m.%Y"))
            task.period = SCHEMA['minfin']['period'][indx]
            task.type_message = TypesNotify.objects.get(id=2)
    elif event.date_of_dicision:
        task.date_finish = event.date_of_dicision + timedelta(days=SCHEMA['first']['term'][is18Topic])
        task.message = SCHEMA['first']['message']
        task.period = SCHEMA['first']['period'][is18Topic]
        task.type_message = TypesNotify.objects.get(id=1)

    if task.message and task.date_finish > now.date():
        task.date_last_update = now
        task.title = f"Уведомление по делу {event}"
        task.target = current_user
        task.save()
        dublicate_chiefs(task)
        return "Уведомления созданы"
    else:
        if task.id is not None:
            task.delete()
        return "Создание уведомлений не требуется"

def dublicate_chiefs(task: NotifyTask):
    now = datetime.now()
    chiefs = CustomUser.objects.filter(UO=True, chief_rule=True)
    date_finish_chief = task.date_finish - timedelta(days=7)
    for chief in chiefs:
        task_chief = NotifyTask(
            content_object = task.content_object,
            system="UO",
            type_message=task.type_message,
            target = chief,
            header="Уведомление Реестра Юридических дел",
            title=f"{task.title} сотрудника {task.target}",
            message=task.message,
            period=(date_finish_chief - now.date()).days,
            date_finish=date_finish_chief,
            date_last_update=now,
        )
        task_chief.save()

def create_new_notify(court) -> NotifyTask:
    return NotifyTask(
            content_object=court,
            system="UO",
            header="Уведомление Реестра Юридических дел",
            date_last_update=datetime.now()
        )