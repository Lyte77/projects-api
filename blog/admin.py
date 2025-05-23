from django.contrib import admin
from .models import Post,Tag

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title','author','created_at']
    search_fields = ['title','tags']