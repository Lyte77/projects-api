from django.db import models

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    technologies = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    project_url = models.URLField(blank=True)
    repository_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title