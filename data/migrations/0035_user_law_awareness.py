# Generated by Django 3.2.8 on 2021-10-22 08:38

import data.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0034_publication_comments_no_max'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='law_awareness',
            field=data.fields.ChoiceArrayField(base_field=models.CharField(choices=[('LAW_AWARENESS_1_CHOICE', 'LAW_AWARENESS_1_TEXT'), ('LAW_AWARENESS_2_CHOICE', 'LAW_AWARENESS_2_TEXT'), ('LAW_AWARENESS_3_CHOICE', 'LAW_AWARENESS_3_TEXT'), ('LAW_AWARENESS_4_CHOICE', 'LAW_AWARENESS_4_TEXT'), ('LAW_AWARENESS_5_CHOICE', 'LAW_AWARENESS_5_TEXT'), ('LAW_AWARENESS_6_CHOICE', 'LAW_AWARENESS_6_TEXT')], max_length=255), blank=True, null=True, size=None, verbose_name='LAW_AWARENESS_DESCRIPTION'),
        ),
    ]
