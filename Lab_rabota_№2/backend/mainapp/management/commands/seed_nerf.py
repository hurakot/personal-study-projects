
#managment - это папка, в которой прописываются собственные команды для управления приложением.

from django.core.management.base import BaseCommand
from mainapp.models import Nerf
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Заполняет базу тестовыми Nerf-пушками"

    def handle(self, *args, **kwargs):
        for i in range(100):
            Nerf.objects.create(
                title=f"Nerf #{i}",
                series=random.choice(["Elite", "Mega", "Ultra"]),
                bullet=random.choice(["Стандарт", "Диски", "Мега"]),
                price=round(random.uniform(10, 200), 2),
                time_create=date.today() - timedelta(days=random.randint(0, 1000)),
                available=random.choice([True, False])
            )

        self.stdout.write(self.style.SUCCESS("✅ Успешно добавлено 100 записей"))