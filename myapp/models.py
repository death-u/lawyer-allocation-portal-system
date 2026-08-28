from django.contrib.auth.models import User
from django.db import models


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/clients/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Client: {self.user.get_full_name() or self.user.username}"


class LawyerProfile(models.Model):
    SPECIALTY_CHOICES = [
        ("family", "Family Law"),
        ("housing", "Housing"),
        ("employment", "Employment Law"),
        ("civil_rights", "Civil Rights"),
        ("criminal", "Criminal Defense"),
    ]

    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("busy", "Busy"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lawyer_profile")
    phone = models.CharField(max_length=15)
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES)
    availability = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES, default="available")
    license_number = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/lawyers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lawyer: {self.user.get_full_name() or self.user.username} ({self.specialty})"

class Case(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="cases")
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="cases")
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=LawyerProfile.SPECIALTY_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"