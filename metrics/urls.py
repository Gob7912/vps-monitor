from django.urls import path
from .views import AddMetric, AlertList

urlpatterns = [
    path('', AddMetric.as_view(), name='metric-create'),
    path('alerts/', AlertList.as_view(), name='alert-list'),
]