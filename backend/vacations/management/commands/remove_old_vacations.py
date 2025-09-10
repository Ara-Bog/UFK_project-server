from django.core.management.base import BaseCommand
from vacations.models import Vacations
from django.utils import timezone

class Command(BaseCommand):
    help = 'Удаление отпусков за прошлый год'

    def handle(self, *args, **kwargs):
        current_year = timezone.now().year
        previous_year = current_year - 1
        
        deleted_count, _ = Vacations.objects.filter(
            date_start__year=previous_year
        ).delete()
        
        self.stdout.write(self.style.SUCCESS(f"Удалено {deleted_count} записей за {previous_year} год"))