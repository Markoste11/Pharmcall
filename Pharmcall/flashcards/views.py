# flashcards/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import UserCard, ReviewHistory  # Include ReviewHistory
from .models import UserCard
import json
from django.core.serializers.json import DjangoJSONEncoder
import random
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render
from django.db.models import Count, Avg
from django.db.models import Q 
from django.views.decorators.csrf import csrf_exempt


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


def home(request):
    return render(request, 'flashcards/home.html')
@login_required
def todays_cards(request):
    if request.user.is_superuser:
        # Superuser can see all UserCards due for review
        user_cards = UserCard.objects.filter(
            next_review_date__lte=timezone.now().date()
        )
    else:
        # Regular users see only their own UserCards
        user_cards = UserCard.objects.filter(
            user=request.user,
            next_review_date__lte=timezone.now().date()
        )

    # Convert queryset to a list
    user_cards_list = list(user_cards)

    # Shuffle the list to randomize the order
    random.shuffle(user_cards_list)

    if request.user.is_superuser:
        # No limit for superuser
        pass
    else:
        # Limit to 3 cards per day for regular users
        user_cards_list = user_cards_list[:3]

    # Prepare data for JSON serialization
    user_cards_json_list = []
    for uc in user_cards_list:
        user_card_data = {
            'uuid': str(uc.uuid),
            'card': {
                'question': uc.card.question,
                'answer': uc.card.answer,
            }
        }
        user_cards_json_list.append(user_card_data)
    user_cards_json = json.dumps(user_cards_json_list)

    context = {
        'user_cards_json': user_cards_json,
    }
    return render(request, 'flashcards/todays_cards.html', context)


@login_required
def update_card_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_uuid = data.get('card_uuid')
        quality = data.get('quality')

        if request.user.is_superuser:
            # Superuser can access any UserCard
            user_card = get_object_or_404(UserCard, uuid=card_uuid)
        else:
            # Regular users can only access their own UserCards
            user_card = get_object_or_404(UserCard, uuid=card_uuid, user=request.user)

        try:
            user_card.update_review(quality)
            return JsonResponse({'status': 'success'})
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def user_stats(request):
    if request.user.is_superuser:
        # Superuser can see all users' statistics
        category_stats = ReviewHistory.objects.values('category').annotate(
            average_quality=Avg('quality'),
            review_count=Count('id')
        )

        medicine_stats = ReviewHistory.objects.values('medicine').annotate(
            average_quality=Avg('quality'),
            review_count=Count('id')
        )
    else:
        # Regular users see only their own statistics
        category_stats = ReviewHistory.objects.filter(user_card__user=request.user).values('category').annotate(
            average_quality=Avg('quality'),
            review_count=Count('id')
        )

        medicine_stats = ReviewHistory.objects.filter(user_card__user=request.user).values('medicine').annotate(
            average_quality=Avg('quality'),
            review_count=Count('id')
        )

    context = {
        'category_stats': category_stats,
        'medicine_stats': medicine_stats,
    }
    return render(request, 'flashcards/user_stats.html', context)
