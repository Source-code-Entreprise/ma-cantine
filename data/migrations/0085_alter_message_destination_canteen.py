# Generated by Django 4.1 on 2022-08-18 08:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0084_user_opt_out_reminder_emails"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="destination_canteen",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="data.canteen",
                verbose_name="destinataire",
            ),
        ),
    ]