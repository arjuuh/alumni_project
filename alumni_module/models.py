from django.db import models
from django.contrib.auth.models import User

class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Personal Info
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)

    # Address Info
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username


class AcademicDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    student_id = models.CharField(max_length=50, blank=True)
    degree = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    year_of_admission = models.IntegerField(null=True, blank=True)
    year_of_graduation = models.IntegerField(null=True, blank=True)
    achievements = models.TextField(blank=True)


class ProfessionalDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    current_designation = models.CharField(max_length=100, blank=True)
    current_company = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    year_of_experience = models.IntegerField(null=True, blank=True)
    company_location = models.CharField(max_length=200, blank=True)
    linkedin_profile = models.URLField(blank=True)
    career_highlights = models.TextField(blank=True)


class ContactDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    alternate_phone = models.CharField(max_length=20, blank=True)

class AlumniEngagement(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    membership_status = models.CharField(max_length=50, blank=True)
    events_attended = models.IntegerField(null=True, blank=True)
    mentorship_interest = models.BooleanField(default=False)
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volunteer_activities = models.TextField(blank=True)
    newsletter_subscription = models.BooleanField(default=False)

    def __str__(self):
        return f"Engagement - {self.user.username}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
    
class Connection(models.Model):
    follower = models.ForeignKey(User, related_name="following_set", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers_set", on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False) 

    
    def __str__(self):
        
        return f"{self.follower.username} follows {self.following.username}"

class Opportunity(models.Model):

    TYPE_CHOICES = (
        ('JOB', 'Job'),
        ('EVENT', 'Event'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    opportunity_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    location = models.CharField(max_length=150, blank=True, null=True)

    deadline = models.DateField(blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.opportunity_type})"
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications", null=True, blank=True)

    message = models.TextField()
    link = models.URLField(blank=True, null=True)

    notification_type = models.CharField(max_length=20, blank=True)  # follow, like, comment

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.user} ({self.notification_type})"

from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name="conversations")
    hidden_for = models.ManyToManyField(User, related_name="hidden_conversations", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        names = ", ".join(self.participants.values_list("username", flat=True)[:3])
        return f"Conversation {self.id} ({names})"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.text[:25]}"
    

import random

class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp():
        return str(random.randint(100000, 999999))
    
from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    apply_link = models.URLField(blank=True, null=True)
    job_type = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title
    
class Event(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    event_type = models.CharField(max_length=100, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    event_time = models.TimeField(blank=True, null=True)
    registration_link = models.URLField(blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title