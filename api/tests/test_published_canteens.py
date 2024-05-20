import os
from django.urls import reverse
from django.core.files import File
from rest_framework.test import APITestCase
from rest_framework import status
from data.factories import CanteenFactory, UserFactory
from data.factories import DiagnosticFactory
from data.models import Canteen, CanteenImage, Diagnostic
from .utils import authenticate

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TestPublishedCanteenApi(APITestCase):
    @authenticate
    def test_canteen_publication_fields_read_only(self):
        """
        Users cannot modify canteen publication status with this endpoint
        """
        canteen = CanteenFactory.create(city="Paris")
        canteen.managers.add(authenticate.user)
        payload = {
            "publication_status": "published",
        }
        response = self.client.patch(reverse("single_canteen", kwargs={"pk": canteen.id}), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        persisted_canteen = Canteen.objects.get(pk=canteen.id)
        self.assertEqual(persisted_canteen.publication_status, Canteen.PublicationStatus.DRAFT.value)

    def test_get_single_published_canteen(self):
        """
        We are able to get a single published canteen.
        """
        published_canteen = CanteenFactory.create(publication_status="published")
        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": published_canteen.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        body = response.json()
        self.assertEqual(body.get("id"), published_canteen.id)

    def test_get_single_unpublished_canteen(self):
        """
        A 404 is raised if we try to get a sinlge published canteen
        that has not been published by the manager.
        """
        private_canteen = CanteenFactory.create()
        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": private_canteen.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @authenticate
    def test_canteen_image_serialization(self):
        """
        A canteen with images should serialize those images
        """
        canteen = CanteenFactory.create(publication_status=Canteen.PublicationStatus.PUBLISHED.value)
        image_names = [
            "test-image-1.jpg",
            "test-image-2.jpg",
            "test-image-3.png",
        ]
        for image_name in image_names:
            path = os.path.join(CURRENT_DIR, f"files/{image_name}")
            with open(path, "rb") as image:
                file = File(image)
                file.name = image_name
                canteen_image = CanteenImage(image=file)
                canteen_image.canteen = canteen
                canteen_image.save()

        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": canteen.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        body = response.json()
        self.assertEqual(len(body.get("images")), 3)

    def test_satellite_published(self):
        central_siret = "22730656663081"
        central_kitchen = CanteenFactory.create(siret=central_siret, production_type=Canteen.ProductionType.CENTRAL)
        satellite = CanteenFactory.create(
            central_producer_siret=central_siret,
            publication_status="published",
            production_type=Canteen.ProductionType.ON_SITE_CENTRAL,
        )

        diagnostic = DiagnosticFactory.create(
            canteen=central_kitchen,
            year=2020,
            value_total_ht=1200,
            value_bio_ht=600,
            diagnostic_type=Diagnostic.DiagnosticType.SIMPLE,
            central_kitchen_diagnostic_mode=Diagnostic.CentralKitchenDiagnosticMode.APPRO,
        )

        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": satellite.id}))
        body = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(body.get("id"), satellite.id)
        self.assertEqual(len(body.get("centralKitchenDiagnostics")), 1)
        self.assertEqual(body.get("centralKitchen").get("id"), central_kitchen.id)

        serialized_diagnostic = body.get("centralKitchenDiagnostics")[0]
        self.assertEqual(serialized_diagnostic["id"], diagnostic.id)
        self.assertEqual(serialized_diagnostic["percentageValueTotalHt"], 1)
        self.assertEqual(serialized_diagnostic["percentageValueBioHt"], 0.5)

    def test_satellite_published_without_bio(self):
        central_siret = "22730656663081"
        central_kitchen = CanteenFactory.create(siret=central_siret, production_type=Canteen.ProductionType.CENTRAL)
        satellite = CanteenFactory.create(
            central_producer_siret=central_siret,
            publication_status="published",
            production_type=Canteen.ProductionType.ON_SITE_CENTRAL,
        )

        diagnostic = DiagnosticFactory.create(
            canteen=central_kitchen,
            year=2020,
            value_total_ht=1200,
            value_bio_ht=None,
            diagnostic_type=Diagnostic.DiagnosticType.SIMPLE,
            central_kitchen_diagnostic_mode=Diagnostic.CentralKitchenDiagnosticMode.APPRO,
        )

        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": satellite.id}))
        body = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(body.get("id"), satellite.id)
        self.assertEqual(len(body.get("centralKitchenDiagnostics")), 1)

        serialized_diagnostic = body.get("centralKitchenDiagnostics")[0]
        self.assertEqual(serialized_diagnostic["id"], diagnostic.id)
        self.assertEqual(serialized_diagnostic["percentageValueTotalHt"], 1)
        self.assertNotIn("percentageValueBioHt", serialized_diagnostic)

    def test_satellite_published_no_type(self):
        """
        Central cuisine diagnostics should only be returned if their central_kitchen_diagnostic_mode
        is set. Otherwise it may be an old diagnostic that is not meant for the satellites
        """
        central_siret = "22730656663081"
        central_kitchen = CanteenFactory.create(siret=central_siret, production_type=Canteen.ProductionType.CENTRAL)
        satellite = CanteenFactory.create(
            central_producer_siret=central_siret,
            publication_status="published",
            production_type=Canteen.ProductionType.ON_SITE_CENTRAL,
        )

        DiagnosticFactory.create(
            canteen=central_kitchen,
            year=2020,
            value_total_ht=1200,
            value_bio_ht=600,
            diagnostic_type=Diagnostic.DiagnosticType.SIMPLE,
            central_kitchen_diagnostic_mode=None,
        )

        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": satellite.id}))
        body = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(body.get("id"), satellite.id)
        self.assertEqual(len(body.get("centralKitchenDiagnostics")), 0)

    def test_satellite_published_needed_fields(self):
        """
        If the central kitchen diag is set to APPRO, only the appro fields should be included.
        If the central kitchen diag is set to ALL, every fields should be included.
        """
        central_siret = "22730656663081"
        central_kitchen = CanteenFactory.create(siret=central_siret, production_type=Canteen.ProductionType.CENTRAL)
        satellite = CanteenFactory.create(
            central_producer_siret=central_siret,
            publication_status="published",
            production_type=Canteen.ProductionType.ON_SITE_CENTRAL,
        )

        DiagnosticFactory.create(
            canteen=central_kitchen,
            year=2020,
            value_total_ht=1200,
            value_bio_ht=600,
            diagnostic_type=Diagnostic.DiagnosticType.SIMPLE,
            central_kitchen_diagnostic_mode=Diagnostic.CentralKitchenDiagnosticMode.APPRO,
        )

        DiagnosticFactory.create(
            canteen=central_kitchen,
            year=2021,
            value_total_ht=1200,
            value_bio_ht=600,
            diagnostic_type=Diagnostic.DiagnosticType.SIMPLE,
            central_kitchen_diagnostic_mode=Diagnostic.CentralKitchenDiagnosticMode.ALL,
            value_fish_ht=100,
            value_fish_egalim_ht=80,
        )

        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": satellite.id}))
        body = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(body.get("centralKitchenDiagnostics")), 2)
        serialized_diagnostics = body.get("centralKitchenDiagnostics")
        serialized_diag_2020 = next(filter(lambda x: x["year"] == 2020, serialized_diagnostics))
        serialized_diag_2021 = next(filter(lambda x: x["year"] == 2021, serialized_diagnostics))

        self.assertIn("percentageValueTotalHt", serialized_diag_2020)
        self.assertNotIn("hasWasteDiagnostic", serialized_diag_2020)

        self.assertIn("percentageValueTotalHt", serialized_diag_2021)
        self.assertIn("hasWasteDiagnostic", serialized_diag_2021)
        self.assertNotIn("valueFishEgalimHt", serialized_diag_2021)
        self.assertIn("percentageValueFishEgalimHt", serialized_diag_2021)

    def test_percentage_values(self):
        """
        The published endpoint should not contain the real economic data, only percentages.
        """
        canteen = CanteenFactory.create(
            production_type=Canteen.ProductionType.ON_SITE,
            publication_status="published",
        )

        DiagnosticFactory.create(
            canteen=canteen,
            year=2021,
            value_total_ht=1200,
            value_bio_ht=600,
            value_sustainable_ht=300,
            value_meat_poultry_ht=200,
            value_meat_poultry_egalim_ht=100,
            value_fish_ht=10,
            value_fish_egalim_ht=8,
            diagnostic_type=Diagnostic.DiagnosticType.SIMPLE,
        )

        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": canteen.id}))
        body = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(body.get("diagnostics")), 1)
        serialized_diag = body.get("diagnostics")[0]

        self.assertEqual(serialized_diag["percentageValueTotalHt"], 1)
        self.assertEqual(serialized_diag["percentageValueBioHt"], 0.5)
        self.assertEqual(serialized_diag["percentageValueSustainableHt"], 0.25)
        # the following is a percentage of the meat total, not global total
        self.assertEqual(serialized_diag["percentageValueMeatPoultryEgalimHt"], 0.5)
        self.assertEqual(serialized_diag["percentageValueFishEgalimHt"], 0.8)
        # ensure the raw values are not included in the diagnostic
        self.assertNotIn("valueTotalHt", serialized_diag)
        self.assertNotIn("valueBioHt", serialized_diag)
        self.assertNotIn("valueMeatPoultryHt", serialized_diag)
        self.assertNotIn("valueMeatPoultryEgalimHt", serialized_diag)
        self.assertNotIn("valueFishHt", serialized_diag)
        self.assertNotIn("valueFishEgalimHt", serialized_diag)

    def test_remove_raw_values_when_missing_totals(self):
        """
        The published endpoint should not contain the real economic data, only percentages.
        Even when the meat and fish totals are absent, but EGAlim and France totals are present.
        """
        central_siret = "22730656663081"
        canteen = CanteenFactory.create(
            siret=central_siret,
            production_type=Canteen.ProductionType.ON_SITE,
            publication_status="published",
        )

        DiagnosticFactory.create(
            canteen=canteen,
            year=2021,
            value_meat_poultry_ht=None,
            value_meat_poultry_egalim_ht=100,
            value_meat_poultry_france_ht=100,
            value_fish_ht=None,
            value_fish_egalim_ht=100,
            diagnostic_type=Diagnostic.DiagnosticType.SIMPLE,
        )

        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": canteen.id}))
        body = response.json()

        serialized_diag = body.get("diagnostics")[0]

        self.assertNotIn("valueMeatPoultryEgalimHt", serialized_diag)
        self.assertNotIn("valueMeatPoultryFranceHt", serialized_diag)
        self.assertNotIn("valueFishEgalimHt", serialized_diag)


class TestPublishedCanteenClaimApi(APITestCase):
    def test_canteen_claim_value(self):
        canteen = CanteenFactory.create(publication_status=Canteen.PublicationStatus.PUBLISHED.value)

        # The factory creates canteens with managers
        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": canteen.id}))
        body = response.json()
        self.assertFalse(body.get("canBeClaimed"))

        # Now we will remove the manager to change the claim API value
        canteen.managers.clear()
        response = self.client.get(reverse("single_published_canteen", kwargs={"pk": canteen.id}))
        body = response.json()
        self.assertTrue(body.get("canBeClaimed"))

    @authenticate
    def test_canteen_claim_request(self):
        canteen = CanteenFactory.create(publication_status=Canteen.PublicationStatus.DRAFT)
        canteen.managers.clear()

        response = self.client.post(reverse("claim_canteen", kwargs={"canteen_pk": canteen.id}), None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["id"], canteen.id)
        self.assertEqual(body["name"], canteen.name)
        user = authenticate.user
        self.assertEqual(canteen.managers.first().id, user.id)
        self.assertEqual(canteen.managers.count(), 1)
        canteen.refresh_from_db()
        self.assertEqual(canteen.claimed_by, user)
        self.assertTrue(canteen.has_been_claimed)

    @authenticate
    def test_canteen_claim_request_fails_when_already_claimed(self):
        canteen = CanteenFactory.create(publication_status=Canteen.PublicationStatus.PUBLISHED.value)
        self.assertGreater(canteen.managers.count(), 0)
        user = authenticate.user
        self.assertFalse(canteen.managers.filter(id=user.id).exists())

        response = self.client.post(reverse("claim_canteen", kwargs={"canteen_pk": canteen.id}), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(canteen.managers.filter(id=user.id).exists())
        canteen.refresh_from_db()
        self.assertFalse(canteen.has_been_claimed)

    @authenticate
    def test_undo_claim_canteen(self):
        canteen = CanteenFactory.create(claimed_by=authenticate.user, has_been_claimed=True)
        canteen.managers.add(authenticate.user)

        response = self.client.post(reverse("undo_claim_canteen", kwargs={"canteen_pk": canteen.id}), None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(canteen.managers.filter(id=authenticate.user.id).exists())
        canteen.refresh_from_db()
        self.assertIsNone(canteen.claimed_by)
        self.assertFalse(canteen.has_been_claimed)

    @authenticate
    def test_undo_claim_canteen_fails_if_not_original_claimer(self):
        other_user = UserFactory.create()
        canteen = CanteenFactory.create(claimed_by=other_user, has_been_claimed=True)
        canteen.managers.add(authenticate.user)

        response = self.client.post(reverse("undo_claim_canteen", kwargs={"canteen_pk": canteen.id}), None)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(canteen.managers.filter(id=authenticate.user.id).exists())
        canteen.refresh_from_db()
        self.assertTrue(canteen.has_been_claimed)
        self.assertEqual(canteen.claimed_by, other_user)
