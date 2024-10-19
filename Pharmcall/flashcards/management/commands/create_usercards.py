# flashcards/management/commands/create_usercards.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from flashcards.models import Card, UserCard
from datetime import date
import uuid

class Command(BaseCommand):
    help = 'Create UserCard instances for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to create UserCards for')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(f"User '{username}' does not exist.")
            return

        cards = Card.objects.all()
        if not cards:
            self.stderr.write("No cards found in the database. Please add cards first.")
            return

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
                self.stdout.write(f"Created UserCard for '{username}' and card: '{card.question}'")
            else:
                self.stdout.write(f"UserCard already exists for '{username}' and card: '{card.question}'")
        self.stdout.write(self.style.SUCCESS('UserCard creation completed successfully.'))
