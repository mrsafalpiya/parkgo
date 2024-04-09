from django.contrib import admin

# Register your models here.
from .models import Vehicle,ParkingSpace

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'registration_number')

class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'owner_phone', 'street_name', 'location',
                     'slots','opening_hours','closing_hours', 'description', 'photo',
                      'vehicle_wash_available' )

admin.site.register(ParkingSpace, ParkingSpaceAdmin)

admin.site.register(Vehicle, VehicleAdmin)
