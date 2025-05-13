from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
     """Serializer for Project model, handling project data and image uploads."""
     image = serializers.ImageField(required=False, allow_null=True)
     class Meta:
        model = Project
        fields = [ 
            'id',
            'title',
            'description',
            'technologies',
            'image',
            'project_url',
            'repository_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

     def validate_title(self, value):
        """Ensure title is unique."""
        instance = self.instance
        queryset = Project.objects.filter(title=value)
        if instance:
            queryset = queryset.exclude(id=instance.id)
        if queryset.exists():
            raise serializers.ValidationError("A project with this title already exists.")
        return value
     
     def validate(self, data):
        """Ensure required fields are provided."""
        if not data.get('title'):
            raise serializers.ValidationError({"title": "This field is required."})
        if not data.get('description'):
            raise serializers.ValidationError({"description": "This field is required."})
        return data