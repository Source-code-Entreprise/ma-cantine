# Generated by Django 5.0.3 on 2024-03-29 16:11

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0141_merge_20240307_1032"),
    ]

    operations = [
        migrations.AddField(
            model_name="videotutorial",
            name="transcription",
            field=ckeditor_uploader.fields.RichTextUploadingField(
                blank=True, null=True, verbose_name="transcription"
            ),
        ),
    ]