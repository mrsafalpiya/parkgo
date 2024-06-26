import math
from django.db.models import Q, Count
from django.http import Http404, JsonResponse, QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ContactUs, ParkingBooking, ParkingPlace, ParkingSpace, Vehicle
import json
from django.core.serializers import (
    serialize,
)
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.utils import timezone
import humanize
import requests


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
            return render(request, "signup.html", context=context)
        users = User.objects.create_user(uname, email, pass1)
        users.save()
        messages.success(request, "User registered successfully.")
        return redirect("login")
        print(uname, "is username")
    return render(request, "signup.html")


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
                messages.success(request, "Welcome to the Park & Go!.")
                return redirect("dashboard")

        # Authentication failed
        messages.error(request, "Invalid email or password")
        error = "Invalid email or password"
        return render(request, "signin.html", {"error": error})

    return render(request, "signin.html")


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
    logout(request)
    return redirect("dashboard")


def about_view(request):
    return render(request, "about.html")


def get_datetime_status(start_datetime, end_datetime):
    current_datetime = timezone.now()

    if current_datetime < start_datetime:
        return "upcoming"
    elif start_datetime <= current_datetime <= end_datetime:
        return "in-progress"
    else:
        return "past"


def booking_view(request):
    user_vehicles = Vehicle.objects.filter(user=request.user)

    context = {}
    bookings = ParkingBooking.objects.filter(vehicle__in=user_vehicles)
    for booking in bookings:
        status = get_datetime_status(booking.arriving_at, booking.exiting_at)
        if status in context:
            context[status].append(booking)
        else:
            context[status] = [booking]

    return render(request, "booking.html", context)


def addvehicle_view(request):
    return render(request, "addvehicle.html")


def details_view(request):
    return render(request, "details.html")


@login_required(login_url="login")
def profile_update(request):
    if request.method == "POST":
        user = request.user
        uname = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")
        if pass1 != pass2:
            messages.error(request, "Password and Confirm password does not match")
            return render(
                request,
                "profile_update.html",
                {"username": user.username, "email": user.email},
            )
        user.username = uname
        user.email = email

        # Check if a new password is provided
        if pass1:
            user.set_password(pass1)
            user.save()
            update_session_auth_hash(request, user)  # Update session to prevent logout
        user.save()
        messages.success(request, "User details updated successfully.")
        return redirect("profile")
    return render(
        request,
        "profile_update.html",
        {"username": request.user.username, "email": request.user.email},
    )


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
    if request.method == "GET":
        return render(request, "contact.html")
    else:
        name = request.POST.get("name")
        mobile_number = request.POST.get("mobile_number")
        email = request.POST.get("email")
        message = request.POST.get("message")

        new_contact_us_details = ContactUs(
            name=name, mobile_number=mobile_number, email=email, message=message
        )
        new_contact_us_details.save()
        return render(request, "contact.html", {"saved": True})


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


@login_required(login_url="login")
def payment(request):
    if request.method == "GET":
        selected_location_id = request.GET.get("selected-location-id")
        arriving_date = request.GET.get("arriving-date")
        exiting_date = request.GET.get("exiting-date")
        arriving_time = request.GET.get("arriving-time")
        exiting_time = request.GET.get("exiting-time")
        slots = request.GET.get("slots")

        location_info = ParkingPlace.objects.get(id=selected_location_id)
        user_vehicles = Vehicle.objects.filter(user=request.user)

        duration = datetime.strptime(
            exiting_date + " " + exiting_time, "%Y-%m-%d %H:%M"
        ) - datetime.strptime(arriving_date + " " + arriving_time, "%Y-%m-%d %H:%M")
        duration_hours = math.ceil(duration.total_seconds() / 3600)

        return render(
            request,
            "details.html",
            {
                "location_info": location_info,
                "arriving_date": arriving_date,
                "exiting_date": exiting_date,
                "arriving_time": arriving_time,
                "exiting_time": exiting_time,
                "duration": humanize.naturaldelta(duration),
                "duration_hours": duration_hours,
                "slots": slots,
                "total_cost": int(slots) * duration_hours * location_info.price,
                "user_vehicles": user_vehicles,
            },
        )
    else:
        selected_location_id = int(request.POST.get("selected-location-id"))
        arriving_date = request.POST.get("arriving-date")
        arriving_time = request.POST.get("arriving-time")
        exiting_date = request.POST.get("exiting-date")
        exiting_time = request.POST.get("exiting-time")
        slots = int(request.POST.get("slots"))
        vehicle = int(request.POST.get("vehicle"))
        wash = bool(request.POST.get("wash") == "true")

        # Create a new booking entry
        place = ParkingPlace.objects.get(id=selected_location_id)
        spaces = ParkingSpace.objects.filter(is_booked=False)[:slots]
        user_vehicle = Vehicle.objects.get(id=vehicle)

        booking_ids = []

        for space in spaces:
            new_booking = ParkingBooking(
                place=place,
                space=space,
                vehicle=user_vehicle,
                arriving_at=datetime.strptime(
                    f"{arriving_date} {arriving_time}", "%Y-%m-%d %H:%M"
                ),
                exiting_at=datetime.strptime(
                    f"{exiting_date} {exiting_time}", "%Y-%m-%d %H:%M"
                ),
                to_wash=wash,
            )
            new_booking.save()
            booking_ids.append(new_booking.pk)

            space.is_booked = True
            space.save()

    q = QueryDict(mutable=True)
    q.setlist("id", booking_ids)
    return redirect("/checkout" + "?" + q.urlencode())


@login_required(login_url="login")
def checkout(request):
    booking_ids = request.GET.getlist("id")
    is_payment_done = request.GET.get("status")
    purchase_order_id = request.GET.get("purchase_order_id")

    if len(booking_ids) == 0 and is_payment_done is None:
        raise Http404

    if purchase_order_id is not None:
        booking_ids_split = purchase_order_id.split("-")
        orders = ParkingBooking.objects.filter(id__in=booking_ids_split)
        orders.update(is_paid=True)

    if request.method == "GET":
        return render(
            request,
            "checkout.html",
            {"is_payment_done": is_payment_done},
        )
    else:
        # Get price
        # ---------

        orders = ParkingBooking.objects.filter(id__in=booking_ids)
        parking_booking = orders[0]
        parking_place = ParkingPlace.objects.get(id=orders[0].place.id)

        price_per_hour = parking_place.price
        wash_price = parking_place.wash_cost

        duration = parking_booking.exiting_at - parking_booking.arriving_at
        duration_hours = math.ceil(duration.seconds / 3600)

        purchase_cost = len(booking_ids) * duration_hours * price_per_hour
        if parking_booking.to_wash:
            purchase_cost += wash_price

        # Construct payload for Khalti
        # ----------------------------

        url = "https://a.khalti.com/api/v2/epayment/initiate/"

        payload = json.dumps(
            {
                "return_url": "http://127.0.0.1:8000/checkout",
                "website_url": "http://127.0.0.1:8000",
                "amount": str(purchase_cost * 100),  # Khalti accepts amount in paisa
                "purchase_order_id": "-".join(booking_ids),
                "purchase_order_name": "Park & Go",
                "customer_info": {
                    "name": request.user.username,
                    "email": request.user.email,
                },
            }
        )
        headers = {
            "Authorization": "key live_secret_key_68791341fdd94846a146f0457ff7b455",
            "Content-Type": "application/json",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return redirect(json.loads(response.text)["payment_url"])


@csrf_exempt
def add_user_vehicle(request):
    json_data = json.loads(request.body)

    vehicle_type = json_data["type"]
    registration_number = json_data["registrationNumber"]
    userId = int(json_data["userId"])

    user = User.objects.get(id=userId)

    new_vehicle = Vehicle(
        user=user,
        vehicle_type=f"{vehicle_type} wheeler",
        registration_number=registration_number,
    )
    new_vehicle.save()

    return JsonResponse({"success": True})


def get_qr_details(booking_id):
    booking_details = ParkingBooking.objects.get(id=booking_id)
    arriving_at = booking_details.arriving_at
    exiting_at = booking_details.exiting_at

    date = arriving_at.strftime("%-d")
    month = arriving_at.strftime("%B")
    day = arriving_at.strftime("%A")
    arriving_time = arriving_at.strftime("%I:%M%p")
    exiting_time = exiting_at.strftime("%I:%M%p")
    to_wash = booking_details.to_wash
    is_paid = booking_details.is_paid

    parking_place = ParkingPlace.objects.get(id=booking_details.place.id)
    price = parking_place.price
    wash_cost = parking_place.wash_cost

    return {
        "id": booking_details.id,
        "date": date,
        "month": month,
        "day": day,
        "arriving_time": arriving_time,
        "exiting_time": exiting_time,
        "price": price,
        "wash_cost": wash_cost,
        "to_wash": to_wash,
        "is_paid": is_paid,
    }


def qr_details(request, booking_id):
    return render(
        request,
        "qr.html",
        get_qr_details(booking_id),
    )


def qr_details_print(request, booking_id):
    return render(
        request,
        "qr-print.html",
        get_qr_details(booking_id),
    )
