from django.shortcuts import render
from rest_framework import viewsets
from .serializers import TestiominialsSerializers
from .models import Testimonial

from rest_framework.permissions import IsAdminUser, AllowAny


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestiominialsSerializers
