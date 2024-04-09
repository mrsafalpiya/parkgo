from django.db import models
from django.contrib.auth.models import User


class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20)


class ParkingSpace(models.Model):
    owner_name = models.CharField(max_length=100)
    owner_phone = models.CharField(max_length=20)
    street_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    slots = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    opening_hours = models.TimeField()
    closing_hours = models.TimeField()
    description = models.TextField()
    photo = models.ImageField(upload_to='uploads/image/')
    vehicle_wash_available = models.BooleanField(default=False)
