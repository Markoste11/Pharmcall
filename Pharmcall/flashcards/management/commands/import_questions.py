# flashcards/management/commands/import_cards.py

from django.core.management.base import BaseCommand
from flashcards.models import Card, UserCard
from django.contrib.auth.models import User
import pandas as pd
import os
from datetime import date
import uuid
from django.db import transaction

class Command(BaseCommand):
    help = 'Import questions and answers from an Excel spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='The path to the Excel file.')
        parser.add_argument('--username', type=str, default='admin', help='Username for the user.')
        parser.add_argument('--password', type=str, default='admin', help='Password for the user.')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        username = kwargs['username']
        password = kwargs['password']

        if not os.path.isfile(excel_file):
            self.stderr.write(f"File {excel_file} does not exist.")
            return

        # Read the Excel file using pandas
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            self.stderr.write(f"Error reading Excel file: {e}")
            return

        # Check that required columns exist
        required_columns = {'Question', 'Answer', 'Medicine', 'Category'}
        if not required_columns.issubset(df.columns):
            self.stderr.write(f"Excel file must contain the following columns: {', '.join(required_columns)}")
            return

        # Begin a transaction to ensure atomicity
        with transaction.atomic():
            # Get a list of current questions in the database
            existing_questions = set(Card.objects.values_list('question', flat=True))

            # Get questions from the Excel file
            excel_questions = set(df['Question'].unique())

            # Determine which cards to delete (if any)
            cards_to_delete = Card.objects.filter(question__in=existing_questions - excel_questions)

            # Delete cards that are no longer in the Excel sheet (optional)
            if cards_to_delete.exists():
                self.stdout.write("Deleting cards no longer in the Excel sheet:")
                for card in cards_to_delete:
                    self.stdout.write(f"Deleting card: {card.question}")
                cards_to_delete.delete()

            # Keep track of new cards created
            new_cards = []

            # Iterate over the rows and update/create Card objects
            for index, row in df.iterrows():
                question = row['Question']
                answer = row['Answer']
                medicine = row['Medicine']
                category = row['Category']

                # Update existing cards or create new ones
                card, created = Card.objects.update_or_create(
                    question=question,
                    defaults={
                        'answer': answer,
                        'medicine': medicine,
                        'category': category
                    }
                )
                if created:
                    self.stdout.write(f"Added new card: {question}")
                    new_cards.append(card)
                else:
                    self.stdout.write(f"Updated existing card: {question}")

            # Get all users
            users = User.objects.all()

            # For all cards, ensure each user has a UserCard
            all_cards = Card.objects.all()
            for user in users:
                for card in all_cards:
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

            self.stdout.write(self.style.SUCCESS('Import and synchronization completed successfully.'))
