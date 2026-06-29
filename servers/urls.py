from django.urls import path
from .views import ServerView, SingleServer

urlpatterns = [
    path('', ServerView.as_view(), name='server-list-create'),
    path('<int:pk>/', SingleServer.as_view(), name='server-detail'),
]