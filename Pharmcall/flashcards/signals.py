from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Card, UserCard
from datetime import date
import uuid

@receiver(post_save, sender=User)
def create_user_cards(sender, instance, created, **kwargs):
    if created:
        # New user has been created
        for card in Card.objects.all():
            UserCard.objects.create(
                user=instance,
                card=card,
                next_review_date=date.today(),
                interval=1,
                repetitions=0,
                ease_factor=2.5,
                uuid=uuid.uuid4()
            )

@receiver(post_save, sender=Card)
def create_card_for_users(sender, instance, created, **kwargs):
    if created:
        # New card has been created
        users = User.objects.all()
        for user in users:
            UserCard.objects.create(
                user=user,
                card=instance,
                next_review_date=date.today(),
                interval=1,
                repetitions=0,
                ease_factor=2.5,
                uuid=uuid.uuid4()
            )
