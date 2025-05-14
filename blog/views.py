from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny,IsAuthenticated
from .serializers import BlogSerializer
from drf_spectacular.utils import extend_schema
from .models import Post

class BlogViewSet(viewsets.ModelViewSet):
      """
        API endpoint for managing blog posts.

        - **GET /api/blog/**: List all published posts (public).
        - **POST /api/blog/**: Create a new post (authenticated users only).
        - **GET /api/blog/{slug}/**: Retrieve a post by slug (public).
        - **PUT /api/blog/{slug}/**: Update a post (author only).
        - **DELETE /api/blog/{slug}/**: Delete a post (author only).
    """

      queryset = Post.objects.all()
      serializer_class = BlogSerializer
      permission_classes = [IsAdminUser]
      lookup_field = 'slug'

      @extend_schema(
        responses={200: BlogSerializer(many=True)},
        description="Retrieve a list of all published blog posts. Accessible to all users."
    )
      def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

      @extend_schema(
        request=BlogSerializer,
        responses={201: BlogSerializer},
        description="Create a new blog post. Requires JWT authentication. Image uploads use multipart/form-data."
    )
      def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

      @extend_schema(
        responses={200: BlogSerializer},
        description="Retrieve a blog post by its slug. Accessible to all users."
    )
      def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

