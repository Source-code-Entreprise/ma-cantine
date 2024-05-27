from django import forms
from django.contrib import admin
from data.models import Teledeclaration
from simple_history.admin import SimpleHistoryAdmin
from .utils import ReadOnlyAdminMixin


class TeledeclarationForm(forms.ModelForm):
    class Meta:
        widgets = {
            "declared_data": forms.Textarea(attrs={"cols": 60, "rows": 5}),
        }


class TeledeclarationInline(admin.TabularInline):
    model = Teledeclaration
    show_change_link = False
    can_delete = False
    fields = ("year", "creation_date", "status", "applicant")
    readonly_fields = fields
    extra = 0


@admin.register(Teledeclaration)
class TeledeclarationAdmin(ReadOnlyAdminMixin, SimpleHistoryAdmin):
    form = TeledeclarationForm
    list_display = (
        "canteen_name",
        "year",
        "applicant",
        "creation_date",
        "status",
    )
    list_filter = ("year", "status")
    fields = (
        "canteen",
        "canteen_siret",
        "year",
        "applicant",
        "diagnostic",
        "creation_date",
        "status",
        "modification_date",
        "declared_data",
        "teledeclaration_mode",
    )
    # want to be able to modify status
    readonly_fields = (
        "canteen",
        "canteen_siret",
        "year",
        "applicant",
        "diagnostic",
        "creation_date",
        "modification_date",
        "declared_data",
        "teledeclaration_mode",
    )
    search_fields = (
        "canteen__name",
        "canteen__siret",
        "applicant__username",
        "applicant__email",
    )

    def canteen_name(self, obj):
        return obj.declared_data["canteen"]["name"]

    # overriding mixin
    def has_change_permission(self, request, obj=None):
        return True
