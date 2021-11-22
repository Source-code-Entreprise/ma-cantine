import csv
import time
import re
import logging
from decimal import Decimal
from data.models.diagnostic import Diagnostic
from django.db import IntegrityError, transaction
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, BadRequest, ValidationError
from django.conf import settings
from rest_framework.generics import UpdateAPIView, CreateAPIView
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.views import APIView
from api.serializers import PublicDiagnosticSerializer, FullCanteenSerializer
from data.models import Canteen, Sector
from api.permissions import IsCanteenManager, CanEditDiagnostic
from .utils import camelize
import requests

logger = logging.getLogger(__name__)


class DiagnosticCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Diagnostic
    serializer_class = PublicDiagnosticSerializer

    def perform_create(self, serializer):
        try:
            canteen_id = self.request.parser_context.get("kwargs").get("canteen_pk")
            canteen = Canteen.objects.get(pk=canteen_id)
            if not IsCanteenManager().has_object_permission(self.request, self, canteen):
                raise PermissionDenied()
            serializer.is_valid(raise_exception=True)
            serializer.save(canteen=canteen)
        except ObjectDoesNotExist:
            logger.error(f"Attempt to create a diagnostic from an unexistent canteen ID : {canteen_id}")
            raise NotFound()
        except IntegrityError:
            logger.error(f"Attempt to create an existing diagnostic for canteen ID {canteen_id}")
            raise BadRequest()


class DiagnosticUpdateView(UpdateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        CanEditDiagnostic,
    ]
    model = Diagnostic
    serializer_class = PublicDiagnosticSerializer
    queryset = Diagnostic.objects.all()

    def put(self, request, *args, **kwargs):
        return JsonResponse({"error": "Only PATCH request supported in this resource"}, status=405)

    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()


# flake8: noqa: C901
class ImportDiagnosticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    value_error_regex = re.compile(r"Field '(.+)' expected .+? got '(.+)'.")
    annotated_sectors = Sector.objects.annotate(name_lower=Lower("name"))

    def post(self, request):
        start = time.time()
        logger.info("Diagnostic bulk import started")
        try:
            with transaction.atomic():
                file = request.data["file"]
                ImportDiagnosticsView._verify_file_size(file)
                (canteens, errors, diagnostics_created) = self._treat_csv_file(file)

                if errors:
                    raise IntegrityError()

            serialized_canteens = [camelize(FullCanteenSerializer(canteen).data) for canteen in canteens.values()]
            return ImportDiagnosticsView._get_success_response(serialized_canteens, diagnostics_created, errors, start)

        except IntegrityError:
            logger.error("L'import du fichier CSV a échoué")
            return ImportDiagnosticsView._get_success_response([], 0, errors, start)

        except ValidationError as e:
            message = e.message
            logger.error(message)
            message = message
            errors = [{"row": 0, "status": 400, "message": message}]
            return ImportDiagnosticsView._get_success_response([], 0, errors, start)

        except Exception as e:
            logger.exception(e)
            message = "Échec lors de la lecture du fichier"
            errors = [{"row": 0, "status": 400, "message": message}]
            return ImportDiagnosticsView._get_success_response([], 0, errors, start)

    @staticmethod
    def _verify_file_size(file):
        if file.size > settings.CSV_IMPORT_MAX_SIZE:
            raise ValidationError("Ce fichier est trop grand, merci d'utiliser un fichier de moins de 10Mo")

    def _treat_csv_file(self, file):
        diagnostics_created = 0
        canteens = {}
        errors = []
        locations_csv_str = "siret,citycode,postcode\n"
        hasLocationsToFind = False

        filestring = file.read().decode("utf-8-sig")
        dialect = csv.Sniffer().sniff(filestring[:1024])

        csvreader = csv.reader(filestring.splitlines(), dialect=dialect)
        for row_number, row in enumerate(csvreader, start=1):
            if row_number == 1 and row[0].lower() == "siret":
                continue
            try:
                if row[0] == "":
                    raise ValidationError({"siret": "Le siret de la cantine ne peut pas être vide"})
                siret = ImportDiagnosticsView._normalise_siret(row[0])
                canteen = self._create_canteen_with_diagnostic(row, siret)
                diagnostics_created += 1
                canteens[canteen.siret] = canteen
                if not canteen.city and (canteen.city_insee_code or canteen.postal_code):
                    # if both city code and postcode are given, use city code and avoid having no location due to mismatch
                    if canteen.city_insee_code:
                        locations_csv_str += f"{canteen.siret},{canteen.city_insee_code},\n"
                    else:
                        locations_csv_str += f"{canteen.siret},,{canteen.postal_code}\n"
                    hasLocationsToFind = True
            except Exception as e:
                for error in self._parse_errors(e, row):
                    errors.append(ImportDiagnosticsView._get_error(e, error["message"], error["code"], row_number))
        if hasLocationsToFind:
            self._update_location_data(canteens, locations_csv_str)
        return (canteens, errors, diagnostics_created)

    @transaction.atomic
    def _create_canteen_with_diagnostic(self, row, siret):
        row[13]  # accessing last column to throw error if badly formatted early on
        if not row[5]:
            raise ValidationError({"daily_meal_count": "Ce champ ne peut pas être vide."})
        elif not row[2] and not row[3]:
            raise ValidationError(
                {"postal_code": "Ce champ ne peut pas être vide si le code INSEE de la ville est vide."}
            )

        # TODO: This should take into account more number formats and be factored out to utils
        number_error_message = "Ce champ doit être un nombre décimal."
        try:
            if not row[11]:
                raise Exception
            value_total_ht = Decimal(row[11].replace(",", "."))
        except Exception as e:
            raise ValidationError({"value_total_ht": number_error_message})

        try:
            if not row[12]:
                raise Exception
            value_bio_ht = Decimal(row[12].replace(",", "."))
        except Exception as e:
            raise ValidationError({"value_bio_ht": number_error_message})

        try:
            if not row[13]:
                raise Exception
            value_sustainable_ht = Decimal(row[13].replace(",", "."))
        except Exception as e:
            raise ValidationError({"value_sustainable_ht": number_error_message})

        (canteen, created) = Canteen.objects.get_or_create(
            siret=siret,
            defaults={
                "siret": siret,
                "name": row[1],
                "city_insee_code": row[2],
                "postal_code": row[3],
                "central_producer_siret": ImportDiagnosticsView._normalise_siret(row[4]),
                "daily_meal_count": row[5],
                "production_type": row[7].lower(),
                "management_type": row[8].lower(),
                "economic_model": row[9].lower(),
            },
        )

        if not created and self.request.user not in canteen.managers.all():
            raise PermissionDenied()

        if created:
            canteen.managers.add(self.request.user)
            if row[6]:
                canteen.sectors.add(
                    *[self.annotated_sectors.get(name_lower__unaccent=sector.lower()) for sector in row[6].split("+")]
                )
            canteen.full_clean()
            canteen.save()

        diagnostic = Diagnostic(
            canteen_id=canteen.id,
            year=row[10],
            value_total_ht=value_total_ht,
            value_bio_ht=value_bio_ht,
            value_sustainable_ht=value_sustainable_ht,
        )
        diagnostic.full_clean()
        diagnostic.save()
        return canteen

    @staticmethod
    def _get_error(e, message, error_status, row_number):
        logger.error(f"Error on row {row_number}")
        logger.exception(e)
        return {"row": row_number, "status": error_status, "message": message}

    @staticmethod
    def _get_success_response(canteens, count, errors, start_time):
        return JsonResponse(
            {
                "canteens": canteens,
                "count": count,
                "errors": errors,
                "seconds": time.time() - start_time,
            },
            status=status.HTTP_200_OK,
        )

    def _parse_errors(self, e, row):
        errors = []
        if isinstance(e, PermissionDenied):
            errors.append(
                {
                    "message": f"Vous n'êtes pas un gestionnaire de cette cantine.",
                    "code": 401,
                }
            )
        elif isinstance(e, Sector.DoesNotExist):
            errors.append(
                {
                    "message": "Le secteur spécifié ne fait pas partie des options acceptées",
                    "code": 400,
                }
            )
        elif isinstance(e, ValidationError):
            if e.message_dict:
                for field, messages in e.message_dict.items():
                    verbose_field_name = ImportDiagnosticsView._get_verbose_field_name(field)
                    for message in messages:
                        user_message = message
                        if user_message == "Un objet Diagnostic avec ces champs Canteen et Année existe déjà.":
                            user_message = "Un diagnostic pour cette année et cette cantine existe déjà."
                        if field != "__all__":
                            user_message = f"Champ '{verbose_field_name}' : {user_message}"
                        errors.append(
                            {
                                "message": user_message,
                                "code": 400,
                            }
                        )

            elif hasattr(e, "params"):
                errors.append(
                    {
                        "message": f"La valeur '{e.params['value']}' n'est pas valide.",
                        "code": 400,
                    }
                )
            else:
                errors.append(
                    {
                        "message": "Une erreur s'est produite en créant un diagnostic pour cette ligne",
                        "code": 400,
                    }
                )
        elif isinstance(e, ValueError):
            match = self.value_error_regex.search(str(e))
            field_name = match.group(1) if match else ""
            value_given = match.group(2) if match else ""
            if field_name:
                verbose_field_name = ImportDiagnosticsView._get_verbose_field_name(field_name)
                errors.append(
                    {
                        "message": f"La valeur '{value_given}' n'est pas valide pour le champ '{verbose_field_name}'.",
                        "code": 400,
                    }
                )
        elif isinstance(e, IndexError):
            errors.append(
                {
                    "message": f"Données manquantes : 14 colonnes attendus, {len(row)} trouvés.",
                    "code": 400,
                }
            )
        if not errors:
            errors.append(
                {
                    "message": "Une erreur s'est produite en créant un diagnostic pour cette ligne",
                    "code": 400,
                }
            )
        return errors

    @staticmethod
    def _normalise_siret(siret):
        return siret.replace(" ", "")

    @staticmethod
    def _get_verbose_field_name(field_name):
        try:
            return Canteen._meta.get_field(field_name).verbose_name
        except:
            try:
                return Diagnostic._meta.get_field(field_name).verbose_name
            except:
                pass
        return field_name

    @staticmethod
    def _update_location_data(canteens, locations_csv_str):
        try:
            # NB: max size of a csv file is 50 MB
            response = requests.post(
                "https://api-adresse.data.gouv.fr/search/csv/",
                files={
                    "data": ("locations.csv", locations_csv_str),
                },
                data={
                    "postcode": "postcode",
                    "citycode": "citycode",
                    "result_columns": ["result_postcode", "result_citycode", "result_city", "result_context"],
                },
                timeout=3,
            )
            response.raise_for_status()  # Raise an exception if the request failed
            for row in csv.reader(response.text.splitlines()):
                if row[0] == "siret":
                    continue  # skip header
                if row[5] != "":  # city found, so rest of data is found
                    canteen = canteens[row[0]]
                    canteen.postal_code = row[3]
                    canteen.city_insee_code = row[4]
                    canteen.city = row[5]
                    canteen.department = row[6].split(",")[0]
                    canteen.save()
        except Exception as e:
            logger.error(f"Error while updating location data : {e}")
