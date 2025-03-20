import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Загрузка всех фикстур в папке'

    def handle(self, *args, **kwargs):
        for app in apps.get_app_configs():
            fixtures_dir = os.path.join(app.path, 'fixtures')
            if os.path.exists(fixtures_dir):
                fixture_files = [f for f in os.listdir(fixtures_dir) if f.endswith('.json')]

                for fixture_file in fixture_files:
                    fixture_path = os.path.join(fixtures_dir, fixture_file)
                    self.stdout.write(f'Загрузка файла: {fixture_path}')
                    call_command('loaddata', fixture_path)

        self.stdout.write(self.style.SUCCESS('Все фикстуры загружены'))