from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ParkingPlace, Vehicle
import json
from django.core.serializers import (
    serialize,
)


# from .models import Users
# Create your views here.
def register_view(request):
    if request.method == "POST":
        error = None
        uname = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")
        if pass1 != pass2:
            error = "Password and Confirm password does not match"
            context = {"errors": error}
            return render(request, "signin.html", context=context)
        users = User.objects.create_user(uname, email, pass1)
        users.save()
        messages.success(request, "User registered successfully.")
        return redirect("login")
        print(uname, "is username")
    return render(request, "signin.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        pass1 = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            # If a user with the provided email exists, authenticate with email and password
            user = authenticate(request, username=user.username, password=pass1)

            if user is not None:
                # Authentication successful, login the user
                login(request, user)
                messages.success(request, "Welcome to the ParkGo!.")
                return redirect("profile")

        # Authentication failed
        error = "Invalid email or password"
        return render(request, "signup.html", {"error": error})

    return render(request, "signup.html")


def dashboard_view(request):
    parking_places = ParkingPlace.objects.annotate(
        num_available_spaces=Count(
            "parkingspace", filter=~Q(parkingspace__is_booked=True)
        )
    )

    context = {}
    context["markers"] = json.loads(
        serialize(
            "geojson",
            parking_places,
        )
    )

    place_spaces_count = {}
    for place in parking_places:
        place_spaces_count[place.id] = place.num_available_spaces
    context["place_spaces_count"] = json.dumps(place_spaces_count)

    return render(request, "index.html", context)


def logout_view(request):
    messages.success(request, "You have been logged out successfully.")
    logout(request)
    return redirect("login")


def about_view(request):
    return render(request, "about.html")


def booking_view(request):
    return render(request, "booking.html")


def addvehicle_view(request):
    return render(request, "addvehicle.html")


def details_view(request):
    return render(request, "details.html")


@login_required(login_url="login")
def profile_view(request):
    user = request.user

    return render(request, "profile.html")


@login_required(login_url="login")
def profile_update(request):
    if request.method == "POST":
        error = None
        user = request.user
        uname = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")
        if pass1 != pass2:
            error = "Password and Confirm password does not match"
            context = {"errors": error}
            return render(request, "profile_update.html", context=context)
        user.username = uname
        user.email = email

        # Check if a new password is provided
        if pass1:
            user.set_password(pass1)
            update_session_auth_hash(request, user)  # Update session to prevent logout
        user.save()
        messages.success(request, "User details updated successfully.")
        return redirect("profile")
    return render(request, "profile_update.html")


@login_required(login_url="login")
def profile_delete(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, "User account deleted successfully.")
        return redirect("dashboard")
    return render(request, "profile.html")


def terms_view(request):
    return render(request, "terms.html")


def works_view(request):
    return render(request, "works.html")


def contact_view(request):
    return render(request, "contact.html")


@login_required(login_url="login")
def addvehicle(request):
    if request.method == "POST":
        v_type = request.POST.get("v_type")
        reg_num = request.POST.get("reg_num")
        user = request.user
        vehicle = Vehicle.objects.create(
            user=user, vehicle_type=v_type, registration_number=reg_num
        )
        vehicle.save()
        messages.success(request, "Vehicle added successfully!")
        # Redirect back to the add vehicle page
        return redirect("addvehicle")
    vehicles = Vehicle.objects.filter(user=request.user)

    return render(request, "addvehicle.html", {"vehicles": vehicles})


@login_required(login_url="login")
def deletevehicle(request, vehicle_id):
    vehicle = Vehicle.objects.get(pk=vehicle_id)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully!")
    return redirect("addvehicle")


@login_required(login_url="login")
def updatevehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == "POST":
        vehicle.vehicle_type = request.POST.get("v_type")
        vehicle.registration_number = request.POST.get("reg_num")
        vehicle.save()
        messages.success(request, "Vehicle updated successfully!")
        return redirect("addvehicle")
    return render(request, "updatevehicle.html", {"vehicle": vehicle})
