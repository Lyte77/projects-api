from django.contrib import admin
from .models import Testimonial

# Register your models here.
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['reviewer_name','reviewer_title']
