# Generated by Django 4.2.7 on 2024-01-10 15:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0132_alter_canteen_department_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="diagnostic",
            name="vegetarian_weekly_recurrence",
            field=models.CharField(
                blank=True,
                choices=[
                    ("NEVER", "Jamais"),
                    ("LOW", "Moins d'une fois par semaine"),
                    ("MID", "Une fois par semaine"),
                    ("HIGH", "Plus d'une fois par semaine"),
                    ("DAILY", "De façon quotidienne"),
                ],
                max_length=255,
                null=True,
                verbose_name="Menus végétariens par semaine",
            ),
        ),
        migrations.AlterField(
            model_name="historicaldiagnostic",
            name="vegetarian_weekly_recurrence",
            field=models.CharField(
                blank=True,
                choices=[
                    ("NEVER", "Jamais"),
                    ("LOW", "Moins d'une fois par semaine"),
                    ("MID", "Une fois par semaine"),
                    ("HIGH", "Plus d'une fois par semaine"),
                    ("DAILY", "De façon quotidienne"),
                ],
                max_length=255,
                null=True,
                verbose_name="Menus végétariens par semaine",
            ),
        ),
    ]
