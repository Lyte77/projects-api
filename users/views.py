from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets
from .models import CustomUser
from .serializers import CreateUserSerializer

# Create your views here.
class CustomObtainAuthToken(ObtainAuthToken):
      """Custom token authentication view that uses email instead of username."""
      def post(self, request, *args, **kwargs):
          serializer = self.serializer_class(data=request.data, context={'request': request})
          serializer.is_valid(raise_exception=True)
          user = serializer.validated_data['user']
          token, created = Token.objects.get_or_create(user=user)
          return Response({
              'token': token.key,
              'email': user.email,
          })
      
class CreateUserView(viewsets.ModelViewSet):
     queryset = CustomUser.objects.all()
     serializer_class = CreateUserSerializer