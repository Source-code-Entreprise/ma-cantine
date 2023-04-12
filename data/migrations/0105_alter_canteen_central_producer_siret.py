# Generated by Django 4.1.7 on 2023-04-12 07:41

import data.models.canteen
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0104_videotutorial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="canteen",
            name="central_producer_siret",
            field=models.TextField(
                blank=True,
                null=True,
                validators=[data.models.canteen.validate_siret],
                verbose_name="siret de la cuisine centrale",
            ),
        ),
    ]
