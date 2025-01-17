# Generated by Django 4.2.1 on 2023-05-30 13:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0112_merge_20230530_1505"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalcanteen",
            name="claimed_by",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Personne qui a revendiqué la cantine",
            ),
        ),
        migrations.AddField(
            model_name="historicalcanteen",
            name="has_been_claimed",
            field=models.BooleanField(
                default=False, verbose_name="cette cantine a été revendiquée"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcanteen",
            name="reservation_expe_participant",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="participante à l'expérimentation réservation",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcanteen",
            name="vegetarian_expe_participant",
            field=models.BooleanField(
                blank=True,
                null=True,
                verbose_name="participante à l'expérimentation repas végétariens",
            ),
        ),
    ]
