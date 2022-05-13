from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField


class LoggedUserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = get_user_model()
        read_only_fields = (
            "id",
            "username",
            "is_staff",
        )
        fields = (
            "id",
            "email",
            "phone_number",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_staff",
            "job",
            "other_job_description",
            "source",
            "other_source_description",
            "creation_mtm_source",
            "creation_mtm_campaign",
            "creation_mtm_medium",
        )


class CanteenManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        read_only_fields = (
            "email",
            "first_name",
            "last_name",
        )
        fields = (
            "email",
            "first_name",
            "last_name",
        )


class BlogPostAuthor(serializers.ModelSerializer):

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "avatar",
        )
