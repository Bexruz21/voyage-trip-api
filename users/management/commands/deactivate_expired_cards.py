from django.core.management.base import BaseCommand
from django.db import models
from django.utils.timezone import now
from users.models import UserMembership


class Command(BaseCommand):
    help = "Деактивирует истёкшие или полностью использованные карты пользователей"

    def handle(self, *args, **kwargs):
        expired_cards = UserMembership.objects.filter(is_active=True).filter(
            models.Q(end_date__lt=now().date()) | models.Q(used_tours__gte=models.F("card__max_tours"))
        )
        count = expired_cards.count()
        for card in expired_cards:
            card.is_active = False
            card.save()
        self.stdout.write(self.style.SUCCESS(f"Деактивировано {count} карт"))
