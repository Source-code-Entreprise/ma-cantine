# Generated by Django 4.0.4 on 2022-05-17 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0071_merge_20220513_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='number_of_managed_cantines',
            field=models.IntegerField(blank=True, null=True, verbose_name="Nombre d'établissements gérés par l'utilisateur"),
        ),
    ]