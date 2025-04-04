from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class Activity(models.Model):
    objects = None
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    node_name = models.CharField(max_length=100)
    activity_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_activities')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='created_activities')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class ActivityUpdate(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='updates')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    progress = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update by {self.user.username} at {self.created_at}"


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('LEAD', 'Team Lead'),
        ('MEMBER', 'Team Member'),
    ]

    # Make sure this field exists and is named exactly 'role'
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='MEMBER'
    )