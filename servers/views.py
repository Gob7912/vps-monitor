from rest_framework import generics, permissions
from .models import Server
from .serializers import ServerSerializer


class ServerListCreateView(generics.ListCreateAPIView):
    serializer_class = ServerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Server.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ServerDetailView(generics.RetrieveAPIView):
    serializer_class = ServerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Server.objects.filter(owner=self.request.user)
