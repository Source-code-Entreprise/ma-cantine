from django.db import models
from django.contrib.auth import get_user_model
from .importtype import ImportType


class ImportError(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="date de création")
    modification_date = models.DateTimeField(auto_now=True, verbose_name="date de modification")

    file = models.FileField(null=True, blank=True, upload_to="import-errors/%Y/%m/%d/", verbose_name="fichier")
    user = models.ForeignKey(
        get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, verbose_name="utilisateur"
    )
    details = models.TextField(null=True, blank=True, verbose_name="détails")
    import_type = models.TextField(null=True, blank=True, choices=ImportType.choices, verbose_name="type d'import")
