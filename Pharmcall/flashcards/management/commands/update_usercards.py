from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from flashcards.models import Card, UserCard
from datetime import date
import uuid

class Command(BaseCommand):
    help = 'Create missing UserCard instances for all users and cards'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        cards = Card.objects.all()

        for user in users:
            for card in cards:
                user_card, created = UserCard.objects.get_or_create(
                    user=user,
                    card=card,
                    defaults={
                        'next_review_date': date.today(),
                        'interval': 1,
                        'repetitions': 0,
                        'ease_factor': 2.5,
                        'uuid': uuid.uuid4()
                    }
                )
                if created:
                    self.stdout.write(f"Created UserCard for user {user.username} and card: {card.question}")
        self.stdout.write(self.style.SUCCESS('UserCard instances updated successfully.'))
