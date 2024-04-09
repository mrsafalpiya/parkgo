from django.contrib.gis import admin
from django.forms import ModelForm, IntegerField
import itertools

# Register your models here.
from .models import ParkingPlace, Vehicle, ParkingSpace


class VehicleAdmin(admin.ModelAdmin):
    list_display = ("user", "vehicle_type", "registration_number")


admin.site.register(ParkingSpace)

admin.site.register(Vehicle, VehicleAdmin)


class CustomGeoWidgetAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {
        "attrs": {
            "default_zoom": 13,
            "default_lon": 85.3240,
            "default_lat": 27.7172,
        },
    }


class ParkingPlaceForm(ModelForm):
    no_of_spaces = IntegerField(required=False)


@admin.register(ParkingPlace)
class MarkerAdmin(CustomGeoWidgetAdmin):
    form = ParkingPlaceForm

    def add_view(self, request, form_url="", extra_context=None):
        self.exclude = ("location_name",)
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().change_view(request, object_id, form_url, extra_context)

    # Remove no of spaces when editing
    def get_fields(self, request, obj):
        if obj is None:
            return super().get_fields(request, obj)
        return tuple(
            item for item in super().get_fields(request, obj) if item != "no_of_spaces"
        )

    # To create no_of_spaces amount of ParkingSpace instances
    def save_related(self, request, form, formsets, change):
        obj = form.instance
        obj.save()

        # Create parking spaces
        if "no_of_spaces" in form.data:
            no_of_spaces = int(form.data["no_of_spaces"])
            ParkingSpace.objects.bulk_create(
                itertools.repeat(ParkingSpace(place=obj), no_of_spaces)
            )

        return super().save_related(request, form, formsets, change)
