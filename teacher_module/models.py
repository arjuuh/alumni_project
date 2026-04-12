from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

DEPARTMENT_CHOICES = [
    ('CS', 'Computer Science'),
    ('MALAYALAM', 'Malayalam'),
    ('ENGLISH', 'English'),
    ('BCOM', 'BCom'),
    ('HISTORY', 'History'),
    ('ECONOMICS', 'Economics'),
    ('ZOOLOGY', 'Zoology'),
    ('POLYMER_CHEMISTRY', 'Polymer Chemistry'),
    ('PLANT_SCIENCE', 'Plant Science'),
    ('MATHS', 'Maths'),
    ('PHYSICS', 'Physics'),
    ('STATISTICS', 'Statistics'),
]

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES)
    is_hod = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.department}"

class Alumni(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    def __str__(self):
        return f"{self.user.username} - {self.status}"
    
from django.db import models
from django.contrib.auth.models import User

class JobPost(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_job_posts")
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=150, blank=True)
    job_type = models.CharField(max_length=50, blank=True)
    apply_link = models.URLField(blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class EventPost(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_event_posts")
    title = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    event_type = models.CharField(max_length=100, blank=True)
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True)
    registration_link = models.URLField(blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

    

