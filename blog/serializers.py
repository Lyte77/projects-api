from .models import Post,Tag
from rest_framework import serializers
from django.utils.text import slugify

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)

    def get_fields(self):
        fields = super().get_fields()
        fields['name'].help_text = "Unique name of the tag (e.g., 'Django')."
        fields['slug'].help_text = "Auto-generated URL-friendly identifier."
        return fields


class BlogSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug','tags',
                   'content', 'featured_image', 'published_at', 'created_at', 'updated_at']
        
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        validated_data['author'] = self.context['request'].user
        validated_data['slug'] = slugify(validated_data['title'])
        post = super().create(validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(slug=slugify(tag_data['name']), defaults=tag_data)
            post.tags.add(tag)
        return post
    
    def get_fields(self):
        fields = super().get_fields()
        fields['title'].help_text = "Unique title of the post (max 200 characters)."
        fields['slug'].help_text = "Auto-generated URL-friendly identifier."
        fields['content'].help_text = "Post content (markdown supported)."
        fields['featured_image'].help_text = "Optional image (upload via multipart/form-data)."
        fields['tags'].help_text = "List of tags to categorize the post."
        fields['published_at'].help_text = "Publication date (null for drafts)."
        return fields