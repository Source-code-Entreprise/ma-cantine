from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from django.core.exceptions import BadRequest, ObjectDoesNotExist
from django.db.models import Sum, Q, Func, F
from django.http import JsonResponse
from api.permissions import IsLinkedCanteenManager
from api.serializers import PurchaseSerializer
from data.models import Purchase, Canteen
import logging

logger = logging.getLogger(__name__)


class PurchasesPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50


class PurchaseListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsLinkedCanteenManager]
    model = Purchase
    serializer_class = PurchaseSerializer
    pagination_class = PurchasesPagination

    def get_queryset(self):
        return Purchase.objects.filter(canteen__in=self.request.user.canteens.all())

    def perform_create(self, serializer):
        canteen_id = self.request.data.get("canteen")
        if not canteen_id:
            logger.error("Canteen ID missing in purchase creation request")
            raise BadRequest("Canteen ID missing in purchase creation request")
        try:
            canteen = Canteen.objects.get(pk=canteen_id)
            if not canteen.managers.filter(pk=self.request.user.pk).exists():
                logger.error(
                    f"User {self.request.user.id} attempted to create a purchase in someone else's canteen: {canteen_id}"
                )
                raise PermissionDenied()
            serializer.save(canteen=canteen)
        except ObjectDoesNotExist as e:
            logger.error(
                f"User {self.request.user.id} attempted to create a purchase in nonexistent canteen {canteen_id}"
            )
            raise NotFound() from e


class PurchaseRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsLinkedCanteenManager]
    model = Purchase
    serializer_class = PurchaseSerializer

    def put(self, request, *args, **kwargs):
        return JsonResponse({"error": "Only PATCH request supported in this resource"}, status=405)

    def get_queryset(self):
        return Purchase.objects.filter(canteen__in=self.request.user.canteens.all())

    def perform_update(self, serializer):
        canteen_id = self.request.data.get("canteen")
        if not canteen_id:
            return serializer.save()
        try:
            canteen = Canteen.objects.get(pk=canteen_id)
            if not canteen.managers.filter(pk=self.request.user.pk).exists():
                logger.error(
                    f"User {self.request.user.id} attempted to update a purchase to someone else's canteen : {canteen_id}"
                )
                raise PermissionDenied()
            serializer.save(canteen=canteen)
        except ObjectDoesNotExist as e:
            logger.error(
                f"User {self.request.user.id} attempted to update a purchase to an nonexistent canteen {canteen_id}"
            )
            raise NotFound() from e


class CanteenPurchasesSummaryView(APIView):
    def get(self, request, *args, **kwargs):
        canteen_id = kwargs.get("canteen_pk")
        year = request.query_params.get("year")
        canteen = Canteen.objects.get(pk=canteen_id)
        purchases = Purchase.objects.filter(canteen=canteen)
        purchases = purchases.filter(date__year=year)
        data = {}
        data["total"] = purchases.aggregate(total=Sum("price_ht"))["total"]
        bio_purchases = purchases.filter(
            Q(characteristics__contains=[Purchase.Characteristic.BIO])
            | Q(characteristics__contains=[Purchase.Characteristic.CONVERSION_BIO])
        ).distinct()
        data["bio"] = bio_purchases.aggregate(total=Sum("price_ht"))["total"]
        # the remaining stats should ignore any bio products
        purchases = purchases.exclude(
            Q(characteristics__contains=[Purchase.Characteristic.BIO])
            | Q(characteristics__contains=[Purchase.Characteristic.CONVERSION_BIO])
        )
        durable_purchases = purchases.annotate(characteristics_len=Func(F("characteristics"), function="CARDINALITY"))
        durable_purchases = durable_purchases.filter(characteristics_len__gt=0)
        data["durable"] = durable_purchases.aggregate(total=Sum("price_ht"))["total"]
        hve_purchases = purchases.filter(characteristics__contains=[Purchase.Characteristic.HVE])
        data["hve"] = hve_purchases.aggregate(total=Sum("price_ht"))["total"]
        aoc_aop_igp_purchases = purchases.filter(
            Q(characteristics__contains=[Purchase.Characteristic.AOCAOP])
            | Q(characteristics__contains=[Purchase.Characteristic.IGP])
        ).distinct()
        data["aocAopIgp"] = aoc_aop_igp_purchases.aggregate(total=Sum("price_ht"))["total"]
        rouge_purchases = purchases.filter(characteristics__contains=[Purchase.Characteristic.LABEL_ROUGE])
        data["rouge"] = rouge_purchases.aggregate(total=Sum("price_ht"))["total"]
        return JsonResponse(data, status=200)
