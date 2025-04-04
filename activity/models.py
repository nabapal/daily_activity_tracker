from django.contrib.auth.models import AbstractUser
from django.db import models

# Role Choices
ROLE_CHOICES = [
    ('super_admin', 'Super Admin'),
    ('team_lead', 'Team Lead'),
    ('team_member', 'Team Member'),
]

class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=[
        ('team_member', 'Team Member'),
        ('team_manager', 'Team Manager'),
        ('super_admin', 'Super Admin'),
    ], default='team_member')

    # Fix the related_name conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",
        blank=True,
    )

    def __str__(self):
        return self.username

class Activity(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('yet_to_start', 'Yet to Start'),
        ('on_hold', 'On Hold'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    node_name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='yet_to_start')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    assigned_users = models.ManyToManyField(CustomUser, related_name="assigned_activities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ActivityUpdate(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="updates")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    update_text = models.TextField()
    update_date = models.DateTimeField(auto_now_add=True)
    status_at_update = models.CharField(max_length=50, choices=Activity.STATUS_CHOICES, default='yet_to_start')

    def __str__(self):
        return f"Update by {self.updated_by.username} on {self.update_date.strftime('%Y-%m-%d %H:%M')}"