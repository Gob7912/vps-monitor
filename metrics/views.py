import os
import requests
from rest_framework import generics, permissions
from .models import Metric, Alert
from .serializers import MetricSerializer, AlertSerializer


def send_telegram_alert(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except requests.exceptions.RequestException:
        pass


class MetricCreateView(generics.CreateAPIView):
    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        metric = serializer.save()
        self.check_and_create_alert(metric)

    def check_and_create_alert(self, metric):
        if metric.cpu_usage > 90:
            Alert.objects.create(
                server=metric.server,
                message=f"CPU usage critical: {metric.cpu_usage}%",
                level='critical'
            )
            send_telegram_alert(
                f"CRITICAL ALERT - Server: {metric.server.name} - CPU usage: {metric.cpu_usage}%"
            )
        if metric.ram_usage > 90:
            Alert.objects.create(
                server=metric.server,
                message=f"RAM usage critical: {metric.ram_usage}%",
                level='critical'
            )
            send_telegram_alert(
                f"CRITICAL ALERT - Server: {metric.server.name} - RAM usage: {metric.ram_usage}%"
            )


class AlertListView(generics.ListAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(server__owner=self.request.user)