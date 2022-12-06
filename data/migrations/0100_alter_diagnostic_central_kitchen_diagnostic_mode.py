# Generated by Django 4.1.3 on 2022-12-05 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0099_remove_teledeclaration_uses_central_kitchen_appro_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="diagnostic",
            name="central_kitchen_diagnostic_mode",
            field=models.CharField(
                blank=True,
                choices=[
                    (
                        "APPRO",
                        "Ce diagnostic concerne les données d'approvisionnement de toutes les cantines satellites",
                    ),
                    (
                        "ALL",
                        "Ce diagnostic concerne toutes les données des cantines satellites",
                    ),
                ],
                max_length=255,
                null=True,
                verbose_name="seulement pertinent pour les cuisines centrales : Quelles données sont déclarées par cette cuisine centrale ?",
            ),
        ),
    ]
