from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class Testimonial(models.Model):
    quote = models.TextField(blank=False)
    reviewer_name = models.CharField(max_length=100,blank=False)
    reviewer_title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['approved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Testimonial by {self.reviewer_name}"
