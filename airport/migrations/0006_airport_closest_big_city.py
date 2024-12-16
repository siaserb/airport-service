# Generated by Django 5.1.4 on 2024-12-11 00:36

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0005_alter_airplane_rows_alter_airplane_seats_in_row_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="airport",
            name="closest_big_city",
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
    ]
