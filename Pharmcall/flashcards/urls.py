from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('cards/', views.todays_cards, name='todays_cards'),
    path('update_review/', views.update_card_review, name='update_card_review'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('stats/', views.user_stats, name='user_stats'),
]
