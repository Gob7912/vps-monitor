from django.urls import path
from .views import MetricCreateView, AlertListView

urlpatterns = [
    path('', MetricCreateView.as_view(), name='metric-create'),
    path('alerts/', AlertListView.as_view(), name='alert-list'),
]