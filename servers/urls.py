from django.urls import path
from .views import ServerListCreateView, ServerDetailView

urlpatterns = [
    path('', ServerListCreateView.as_view(), name='server-list-create'),
    path('<int:pk>/', ServerDetailView.as_view(), name='server-detail'),
]