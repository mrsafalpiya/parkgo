from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
import requests
import json


class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20)


class ParkingPlace(models.Model):
    location_name = models.CharField(max_length=255)
    location = models.PointField()
    parking_name = models.CharField(
        max_length=255,
        help_text="More specific name of the parking area. Helps user find/get details of the location. For example: City Center",
    )
    photo = models.ImageField(upload_to="uploads/image/")
    vehicle_wash_available = models.BooleanField(default=False)
    wash_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    opening_hours = models.TimeField()
    closing_hours = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.location_name)

    @staticmethod
    def pre_save(sender, instance, **kwargs):
        if instance.location_name == "":
            res = requests.get(
                f"https://geocode.maps.co/reverse?api_key=65a96648e1cd3020225512hcq628bd0&lon={instance.location.coords[0]}&lat={instance.location.coords[1]}"
            )
            response = json.loads(res.text)

            if "suburb" in response["address"]:
                instance.location_name = response["address"]["suburb"]
            elif "neighbourhood" in response["address"]:
                instance.location_name = response["address"]["neighbourhood"]
            else:
                instance.location_name = response["address"]["city_district"]


pre_save.connect(ParkingPlace.pre_save, ParkingPlace)


class ParkingSpace(models.Model):
    place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.place.parking_name} - #{self.pk}"


class ParkingBooking(models.Model):
    place = models.ForeignKey(ParkingPlace, on_delete=models.CASCADE)
    space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    arriving_at = models.DateTimeField()
    exiting_at = models.DateTimeField()

    to_wash = models.BooleanField()

    is_paid = models.BooleanField(default=False)


class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.mobile_number}"

    class Meta:
        verbose_name_plural = "Contact us"
