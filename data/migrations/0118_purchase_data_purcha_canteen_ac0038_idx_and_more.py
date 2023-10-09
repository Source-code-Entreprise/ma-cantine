# Generated by Django 4.2.1 on 2023-07-11 15:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0117_canteen_data_cantee_central_5c2299_idx"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="purchase",
            index=models.Index(
                fields=["canteen"], name="data_purcha_canteen_ac0038_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="purchase",
            index=models.Index(
                fields=["import_source"], name="data_purcha_import__b69540_idx"
            ),
        ),
    ]