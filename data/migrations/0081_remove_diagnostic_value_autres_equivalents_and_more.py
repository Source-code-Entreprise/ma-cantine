# Generated by Django 4.0.5 on 2022-07-04 19:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0080_diagnostic_value_autres_aocaop_igp_stg_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_autres_equivalents',
        ),
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_boissons_equivalents',
        ),
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_boulangerie_equivalents',
        ),
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_charcuterie_equivalents',
        ),
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_fruits_et_legumes_equivalents',
        ),
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_produits_de_la_mer_equivalents',
        ),
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_produits_laitiers_equivalents',
        ),
        migrations.RemoveField(
            model_name='diagnostic',
            name='value_viandes_volailles_equivalents',
        ),
    ]