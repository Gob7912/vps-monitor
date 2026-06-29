from rest_framework import generics, permissions
from .serializers import RegisterSerializer

class SignUp(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
