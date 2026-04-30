from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Member(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('Ushering', 'Ushering'),
        ('Choir', 'Choir'),
        ('Prayer', 'Prayer'),
        ('Youth', 'Youth'),
        ('Children', 'Children'),
        ('Media', 'Media'),
        ('Welfare', 'Welfare'),
        ('None', 'None'),
    ]
    
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='None')
    date_joined = models.DateField(default=timezone.now)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    service_type = models.CharField(max_length=50, default='Sunday Service')
    notes = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.member.name} - {self.date} - {self.status}"
    
    class Meta:
        ordering = ['-date', 'member__name']
        unique_together = ['member', 'date', 'service_type']


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_posted']
