# Generated by Django 4.2.7 on 2024-01-09 17:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0132_alter_canteen_department_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="diagnostic",
            name="duration_leftovers_measurement",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MaxValueValidator(365)],
                verbose_name="période de mesure (jours)",
            ),
        ),
        migrations.AddField(
            model_name="diagnostic",
            name="total_leftovers",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="total des déchets alimentaires (t)",
            ),
        ),
        migrations.AddField(
            model_name="historicaldiagnostic",
            name="duration_leftovers_measurement",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MaxValueValidator(365)],
                verbose_name="période de mesure (jours)",
            ),
        ),
        migrations.AddField(
            model_name="historicaldiagnostic",
            name="total_leftovers",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="total des déchets alimentaires (t)",
            ),
        ),
    ]
