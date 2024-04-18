from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard_view, name="dashboard"),
    path("about/", views.about_view, name="about"),
    path("profile/", views.profile_view, name="profile"),
    path("terms/", views.terms_view, name="terms"),
    path("works/", views.works_view, name="works"),
    path("booking/", views.booking_view, name="booking"),
    path("details/", views.details_view, name="details"),
    path("contact/", views.contact_view, name="contact"),
    path("profile_update/", views.profile_update, name="profile_update"),
    path("profile_delete", views.profile_delete, name="profile_delete"),
    path("addvehicle/", views.addvehicle, name="addvehicle"),
    path("deletevehicle/<int:vehicle_id>", views.deletevehicle, name="deletevehicle"),
    path("updatevehicle/<int:vehicle_id>", views.updatevehicle, name="updatevehicle"),
    path("payment", views.payment, name="payment"),
    path("checkout", views.checkout, name="checkout"),
    path("add-vehicle", views.add_user_vehicle, name="payment"),
    path("qr/<int:booking_id>", views.qr_details, name="qr"),
    path("qr-print/<int:booking_id>", views.qr_details_print, name="qr-print"),
]
