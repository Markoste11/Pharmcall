from datetime import timedelta, date

def calculate_next_review(user_card, quality):
    # SM2 algorithm implementation
    quality = int(quality)
    if quality < 3:
        user_card.repetitions = 0
        user_card.interval = 1
    else:
        user_card.repetitions += 1
        if user_card.repetitions == 1:
            user_card.interval = 1
        elif user_card.repetitions == 2:
            user_card.interval = 6
        else:
            user_card.interval = int(user_card.interval * user_card.ease_factor)
        user_card.ease_factor = user_card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if user_card.ease_factor < 1.3:
            user_card.ease_factor = 1.3
    user_card.next_review_date = date.today() + timedelta(days=user_card.interval)
    user_card.last_reviewed = date.today()
    user_card.save()
