# Generated by Django 5.0.2 on 2024-04-09 20:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_project", "0002_parkingspace_is_booked"),
    ]

    operations = [
        migrations.AddField(
            model_name="parkingplace",
            name="wash_cost",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.CreateModel(
            name="ParkingBooking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("arriving_at", models.DateTimeField()),
                ("exiting_at", models.DateTimeField()),
                ("to_wash", models.BooleanField()),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth_project.parkingplace",
                    ),
                ),
                (
                    "space",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth_project.parkingspace",
                    ),
                ),
            ],
        ),
    ]