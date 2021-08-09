import logging
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.db import transaction, IntegrityError
from rest_framework.generics import RetrieveAPIView, ListAPIView, ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework import permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from api.serializers import (
    PublicCanteenSerializer,
    FullCanteenSerializer,
    ManagingTeamSerializer,
)
from data.models import Canteen, ManagerInvitation
from api.permissions import IsCanteenManager
from .utils import camelize

logger = logging.getLogger(__name__)


class PublishedCanteensPagination(LimitOffsetPagination):
    default_limit = 12
    max_limit = 30


class PublishedCanteensView(ListAPIView):
    model = Canteen
    serializer_class = PublicCanteenSerializer
    queryset = Canteen.objects.filter(publication_status="published")
    pagination_class = PublishedCanteensPagination


class PublishedCanteenSingleView(RetrieveAPIView):
    model = Canteen
    serializer_class = PublicCanteenSerializer
    queryset = Canteen.objects.filter(publication_status="published")


class UserCanteensView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Canteen
    serializer_class = FullCanteenSerializer

    def get_queryset(self):
        return self.request.user.canteens.all()

    def perform_create(self, serializer):
        canteen = serializer.save()
        canteen.managers.add(self.request.user)


class UpdateUserCanteenView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCanteenManager]
    model = Canteen
    serializer_class = FullCanteenSerializer
    queryset = Canteen.objects.all()

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {"error": "Only PATCH request supported in this resource"}, status=405
        )

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        is_draft = serializer.instance.publication_status == "draft"
        publication_requested = (
            serializer.validated_data.get("publication_status") == "pending"
        )

        if is_draft and publication_requested:
            protocol = "https" if settings.SECURE else "http"
            canteen = serializer.instance
            admin_url = "{}://{}/admin/data/canteen/{}/change/".format(
                protocol, settings.HOSTNAME, canteen.id
            )

            logger.info(f"Demande de publication de {canteen.name} (ID: {canteen.id})")

            send_mail(
                "Demande de publication sur ma cantine",
                f"La cantine « {canteen.name} » a demandé d'être publiée.\nAdmin : {admin_url}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=True,
            )

        return super(UpdateUserCanteenView, self).perform_update(serializer)


def _respond_with_team(canteen):
    data = ManagingTeamSerializer(canteen).data
    return JsonResponse(camelize(data), status=status.HTTP_200_OK)


class AddManagerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            validate_email(email)
            canteen_id = request.data.get("canteen_id")
            canteen = request.user.canteens.get(id=canteen_id)
            try:
                user = get_user_model().objects.get(email=email)
                canteen.managers.add(user)
            except get_user_model().DoesNotExist:
                with transaction.atomic():
                    pm = ManagerInvitation(canteen_id=canteen.id, email=email)
                    pm.save()
                AddManagerView._send_invitation_email(pm)
            return _respond_with_team(canteen)
        except ValidationError as e:
            logger.error(f"Attempt to add manager with invalid email {email}")
            logger.exception(e)
            return JsonResponse(
                {"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Canteen.DoesNotExist as e:
            logger.error(f"Attempt to add manager to unexistent canteen {canteen_id}")
            logger.exception(e)
            return JsonResponse(
                {"error": "Invalid canteen id"}, status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError as e:
            logger.error(
                f"Attempt to add existing manager with email {email} to canteen {canteen_id}"
            )
            logger.exception(e)
            return _respond_with_team(canteen)
        except Exception as e:
            logger.error("Exception ocurred while inviting a manager to canteen")
            logger.exception(e)
            return JsonResponse(
                {"error": "An error has ocurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def _send_invitation_email(manager_invitation):
        try:
            template = "auth/manager_invitation"
            context = {
                "canteen": manager_invitation.canteen.name,
                "protocol": "https" if settings.SECURE_SSL_REDIRECT else "http",
                "domain": settings.HOSTNAME,
            }
            send_mail(
                subject="Invitation à gérer une cantine sur ma cantine",
                message=render_to_string(f"{template}.txt", context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=render_to_string(f"{template}.html", context),
                recipient_list=[manager_invitation.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error("The manager invitation email could not be sent:")
            logger.exception(e)
            raise Exception("Error occurred : the mail could not be sent.") from e


class RemoveManagerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            validate_email(email)
            canteen_id = request.data.get("canteen_id")
            canteen = request.user.canteens.get(id=canteen_id)

            try:
                manager = get_user_model().objects.get(email=email)
                canteen.managers.remove(manager)
            except get_user_model().DoesNotExist:
                try:
                    invitation = ManagerInvitation.objects.get(
                        canteen_id=canteen.id, email=email
                    )
                    invitation.delete()
                except ManagerInvitation.DoesNotExist:
                    pass
            return _respond_with_team(canteen)
        except ValidationError as e:
            logger.error(f"Attempt to remove manager with invalid email {email}")
            logger.exception(e)
            return JsonResponse(
                {"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Canteen.DoesNotExist as e:
            logger.error(
                f"Attempt to remove manager from unexistent canteen {canteen_id}"
            )
            logger.exception(e)
            return JsonResponse(
                {"error": "Invalid canteen id"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error("Exception ocurred while removing a manager from a canteen")
            logger.exception(e)
            return JsonResponse(
                {"error": "An error has ocurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendCanteenEmailView(APIView):
    def post(self, request):
        try:
            email = request.data.get("from")
            validate_email(email)

            canteen_id = request.data.get("canteen_id")
            canteen = Canteen.objects.get(pk=canteen_id)

            template = "contact_canteen"
            context = {
                "canteen": canteen.name,
                "from": email,
                "name": request.data.get("name") or "Une personne",
                "message": request.data.get("message"),
                "us": settings.DEFAULT_FROM_EMAIL,
                "repliesToTeam": False,
            }
            recipients = [user.email for user in canteen.managers.all()]
            recipients.append(settings.DEFAULT_FROM_EMAIL)

            reply_to = recipients.copy()
            reply_to.append(email)

            subject = f"Un message pour {canteen.name}"
            from_email = settings.DEFAULT_FROM_EMAIL
            html_content = render_to_string(f"{template}.html", context)
            text_content = render_to_string(f"{template}.txt", context)

            message = EmailMultiAlternatives(
                subject, text_content, from_email, recipients, reply_to=reply_to
            )
            message.attach_alternative(html_content, "text/html")
            message.send()

            return JsonResponse({}, status=status.HTTP_200_OK)
        except ValidationError:
            return JsonResponse(
                {"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                {"error": "Invalid canteen"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return JsonResponse(
                {"error": "An error has ocurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
