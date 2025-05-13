from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from .serializers import ProjectSerializer
from rest_framework.response import Response

from .models import Project

# Create your views here.

class ProjectViewSet(viewsets.ModelViewSet):

    """API endpoints for managing projects.

    - GET /api/projects/: List all projects (public).
    - GET /api/projects/<id>/: Retrieve a project (public).
    - POST /api/projects/: Create a project (admin only).
    - PUT/PATCH /api/projects/<id>/: Update a project (admin only).
    - DELETE /api/projects/<id>/: Delete a project (admin only).
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        """Allow public read access, restrict write actions to admins."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]