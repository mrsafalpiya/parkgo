# Generated by Django 5.0.2 on 2024-04-16 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_project", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="parkingbooking",
            name="is_paid",
            field=models.BooleanField(default=False),
        ),
    ]
