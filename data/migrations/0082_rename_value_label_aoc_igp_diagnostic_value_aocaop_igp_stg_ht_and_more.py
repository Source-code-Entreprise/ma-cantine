# Generated by Django 4.0.6 on 2022-07-12 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0081_remove_diagnostic_value_autres_equivalents_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='diagnostic',
            old_name='value_label_aoc_igp',
            new_name='value_aocaop_igp_stg_ht',
        ),
        migrations.RenameField(
            model_name='diagnostic',
            old_name='value_label_hve',
            new_name='value_hve_ht',
        ),
        migrations.RenameField(
            model_name='diagnostic',
            old_name='value_label_rouge',
            new_name='value_label_rouge_ht',
        ),
    ]
