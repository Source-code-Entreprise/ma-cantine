# Generated by Django 3.2.11 on 2022-01-19 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0040_alter_user_law_awareness'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('name', models.TextField()),
            ],
            options={
                'verbose_name': 'étiquette de blog',
                'verbose_name_plural': 'étiquettes de blog',
            },
        ),
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=models.ManyToManyField(blank=True, to='data.BlogTag', verbose_name='étiquettes'),
        ),
    ]