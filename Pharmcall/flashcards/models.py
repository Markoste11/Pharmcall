from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date, timedelta

class Card(models.Model):
    question = models.TextField()
    answer = models.TextField()
    medicine = models.CharField(max_length=100, null=True, blank=True)  # Allow null and blank
    category = models.CharField(max_length=100, null=True, blank=True)  # Allow null and blank

    def __str__(self):
        return self.question



class UserCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    next_review_date = models.DateField()
    interval = models.IntegerField(default=1)  # in days
    repetitions = models.IntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)
    last_reviewed = models.DateField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.user.username} - {self.card.question}"

    def update_review(self, quality):
        """
        Updates the card's review data based on the user's response quality.

        :param quality: An integer between 0 and 5 indicating the quality of recall.
                        5 - perfect response
                        0 - complete blackout
        """
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5.")

        # If the quality response is less than 3, reset repetitions
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)

        # Update ease factor
        self.ease_factor = self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if self.ease_factor < 1.3:
            self.ease_factor = 1.3

        # Set next review date
        self.next_review_date = date.today() + timedelta(days=self.interval)

        # Update last reviewed date
        self.last_reviewed = date.today()

        # Save the changes
        self.save()

        # Record the review in history
        ReviewHistory.objects.create(
        user_card=self,
        quality=quality,
        interval=self.interval,
        ease_factor=self.ease_factor,
        medicine=self.card.medicine,
        category=self.card.category
    )

class ReviewHistory(models.Model):
    user_card = models.ForeignKey(UserCard, on_delete=models.CASCADE)
    review_date = models.DateTimeField(auto_now_add=True)
    quality = models.IntegerField()
    interval = models.IntegerField()
    ease_factor = models.FloatField()
    medicine = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Review of {self.user_card.card} on {self.review_date}"
