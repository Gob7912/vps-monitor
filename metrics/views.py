import os
import requests
from rest_framework import generics, permissions
from .models import Metric, Alert
from .serializers import MetricSerializer, AlertSerializer

def send_telegram(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except requests.exceptions.RequestException:
        pass


class AddMetric(generics.CreateAPIView):
    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        m = serializer.save()
        self.make_alert(m)

    def make_alert(self, m):
        if m.cpu_usage > 90:
            Alert.objects.create(
                server=m.server,
                message=f"CPU usage critical: {m.cpu_usage}%",
                level='critical'
            )
            send_telegram(
                f"CRITICAL - Server: {m.server.name} - CPU: {m.cpu_usage}%"
            )
        if m.ram_usage > 90:
            Alert.objects.create(
                server=m.server,
                message=f"RAM usage critical: {m.ram_usage}%",
                level='critical'
            )
            send_telegram(
                f"CRITICAL - Server: {m.server.name} - RAM: {m.ram_usage}%"
            )


class AlertList(generics.ListAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(server__owner=self.request.user)
