# Generated by Django 4.0.2 on 2022-02-24 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0049_purchase_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='canteen',
            name='satellite_canteens_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='nombre de cantines satellites dépendantes (si cuisine centrale)'),
        ),
        migrations.AlterField(
            model_name='canteen',
            name='production_type',
            field=models.CharField(blank=True, choices=[('central', 'Cuisine centrale sans lieu de consommation'), ('central_serving', 'Cuisine centrale qui accueille aussi des convives sur place'), ('site', 'Cantine qui produit les repas sur place'), ('site_cooked_elsewhere', 'Cantine qui sert des repas preparés par une cuisine centrale')], max_length=255, null=True, verbose_name='mode de production'),
        ),
    ]