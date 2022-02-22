from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from data.department_choices import Department
from data.factories import CanteenFactory, SectorFactory
from data.factories import DiagnosticFactory
from data.models import Canteen, Diagnostic
from api.views.canteen import badges_for_queryset
from data.region_choices import Region


class TestCanteenStatsApi(APITestCase):
    def test_canteen_statistics(self):
        """
        This public endpoint returns some summary statistics for a region and a location
        """
        # TODO: more nuance when choosing canteens to get stats for?
        # How do we know that the canteen diagnostic is done?
        # Could check for total value ht

        # create 5 canteens (3 in region of interest), 1 unpublished
        region = "01"
        year = 2020
        school = SectorFactory.create(name="School")
        enterprise = SectorFactory.create(name="Enterprise")
        social = SectorFactory.create(name="Social")

        published = CanteenFactory.create(
            region=region,
            publication_status=Canteen.PublicationStatus.PUBLISHED.value,
            sectors=[school, enterprise],
            daily_meal_count=50,
        )
        unpublished = CanteenFactory.create(
            region=region,
            publication_status=Canteen.PublicationStatus.DRAFT.value,
            sectors=[school],
            daily_meal_count=50,
        )
        other_region = CanteenFactory.create(region="03", sectors=[social], daily_meal_count=50)

        # relevant diagnostics
        DiagnosticFactory.create(
            canteen=published,
            year=year,
            value_total_ht=100,
            value_bio_ht=20,
            value_sustainable_ht=30,
            has_waste_diagnostic=False,
            waste_actions=[],
            vegetarian_weekly_recurrence=Diagnostic.MenuFrequency.DAILY,
            plastic_tableware_substituted=False,
            communicates_on_food_quality=False,
        )
        DiagnosticFactory.create(
            canteen=unpublished,
            year=year,
            value_total_ht=1000,
            value_bio_ht=400,
            value_sustainable_ht=500,
            has_waste_diagnostic=True,
            waste_actions=["action1", "action2"],
            vegetarian_weekly_recurrence=Diagnostic.MenuFrequency.LOW,
            cooking_plastic_substituted=True,
            serving_plastic_substituted=True,
            plastic_bottles_substituted=True,
            plastic_tableware_substituted=True,
            communicates_on_food_quality=True,
        )
        # irrelevant diagnostics
        DiagnosticFactory.create(
            canteen=published,
            year=2019,
            value_total_ht=100,
            value_bio_ht=100,
            value_sustainable_ht=0,
            vegetarian_weekly_recurrence=Diagnostic.MenuFrequency.DAILY,
        )
        DiagnosticFactory.create(
            canteen=other_region,
            year=year,
            value_total_ht=100,
            value_bio_ht=100,
            value_sustainable_ht=0,
            cooking_plastic_substituted=True,
            serving_plastic_substituted=True,
            plastic_bottles_substituted=True,
            plastic_tableware_substituted=True,
            communicates_on_food_quality=True,
        )

        response = self.client.get(reverse("canteen_statistics"), {"region": region, "year": year})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        body = response.json()
        self.assertEqual(body["canteenCount"], 2)
        self.assertEqual(body["publishedCanteenCount"], 1)
        self.assertEqual(body["bioPercent"], 30)
        self.assertEqual(body["sustainablePercent"], 40)
        self.assertEqual(body["approPercent"], 100)
        self.assertEqual(body["wastePercent"], 50)
        self.assertEqual(body["diversificationPercent"], 50)
        self.assertEqual(body["plasticPercent"], 50)
        self.assertEqual(body["infoPercent"], 50)
        expected_sectors = {}
        expected_sectors[str(school.id)] = 2
        expected_sectors[str(enterprise.id)] = 1
        expected_sectors[str(social.id)] = 0
        self.assertEqual(body["sectors"], expected_sectors)

        # can also call without location info
        response = self.client.get(reverse("canteen_statistics"), {"year": 2020})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_canteen_stats_by_department(self):
        department = "01"
        year = 2020
        CanteenFactory.create(department=department, publication_status=Canteen.PublicationStatus.PUBLISHED.value)

        response = self.client.get(reverse("canteen_statistics"), {"department": department, "year": year})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        body = response.json()
        self.assertEqual(body["canteenCount"], 1)

    def test_canteen_stats_missing_data(self):
        response = self.client.get(reverse("canteen_statistics"), {"region": "01"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(reverse("canteen_statistics"), {"department": "01"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_appro_badge_earned(self):
        """
        Test that the right canteens are identified in appro badge queryset
        """
        # --- Canteens which don't earn appro badge:
        zero_total = CanteenFactory.create()
        DiagnosticFactory.create(canteen=zero_total, value_total_ht=0)
        null_total = CanteenFactory.create()
        DiagnosticFactory.create(canteen=null_total, value_total_ht=None)
        bio_lacking = CanteenFactory.create()
        DiagnosticFactory.create(canteen=bio_lacking, value_total_ht=100, value_bio_ht=19, value_sustainable_ht=31)
        # not convinced the following shouldn't get a badge but not sure how to make the Sum function work
        null_sustainable = CanteenFactory.create(region=Region.ile_de_france.value)
        DiagnosticFactory.create(
            canteen=null_sustainable, value_total_ht=100, value_bio_ht=50, value_sustainable_ht=None
        )

        # --- Canteens which earn appro badge:
        earned = CanteenFactory.create()
        DiagnosticFactory.create(canteen=earned, value_total_ht=100, value_bio_ht=20, value_sustainable_ht=30)
        # rules per outre mer territories
        guadeloupe = CanteenFactory.create(region=Region.guadeloupe.value)
        DiagnosticFactory.create(canteen=guadeloupe, value_total_ht=100, value_bio_ht=5, value_sustainable_ht=15)
        mayotte = CanteenFactory.create(region=Region.mayotte.value)
        DiagnosticFactory.create(canteen=mayotte, value_total_ht=100, value_bio_ht=2, value_sustainable_ht=3)
        # TODO: rules per outre mer territories: Saint-Pierre-et-Miquelon
        # st_pierre_et_miquelon = CanteenFactory.create(region=Region.st_pierre_et_miquelon.value)
        # DiagnosticFactory.create(canteen=st_pierre_et_miquelon, value_total_ht=100, value_bio_ht=10, value_sustainable_ht=20)

        badges = badges_for_queryset(Diagnostic.objects.all())

        appro_badge_qs = badges["appro"]
        self.assertTrue(appro_badge_qs.filter(canteen=earned).exists())
        self.assertTrue(appro_badge_qs.filter(canteen=guadeloupe).exists())
        self.assertTrue(appro_badge_qs.filter(canteen=mayotte).exists())
        self.assertEqual(appro_badge_qs.count(), 3)

    def test_waste_badge_earned(self):
        """
        Test that the right canteens are identifies in waste badge qs
        """
        # --- Canteens which don't earn waste badge:
        waste_actions_only = CanteenFactory.create(daily_meal_count=2999)
        DiagnosticFactory.create(canteen=waste_actions_only, has_waste_diagnostic=False, waste_actions=["action1"])
        waste_diagnostic_only = CanteenFactory.create(daily_meal_count=2999)
        DiagnosticFactory.create(canteen=waste_diagnostic_only, has_waste_diagnostic=True, waste_actions=[])
        large_canteen_no_badge = CanteenFactory.create(daily_meal_count=3000)
        DiagnosticFactory.create(
            canteen=large_canteen_no_badge,
            has_waste_diagnostic=True,
            waste_actions=["action1"],
            has_donation_agreement=False,
        )
        # --- Canteens which earn waste badge:
        small_canteen = CanteenFactory.create(daily_meal_count=2999)
        DiagnosticFactory.create(canteen=small_canteen, has_waste_diagnostic=True, waste_actions=["action1"])
        large_canteen = CanteenFactory.create(daily_meal_count=3000)
        DiagnosticFactory.create(
            canteen=large_canteen, has_waste_diagnostic=True, waste_actions=["action1"], has_donation_agreement=True
        )

        badges = badges_for_queryset(Diagnostic.objects.all())

        waste_badge_qs = badges["waste"]
        self.assertEqual(waste_badge_qs.count(), 2)
        self.assertTrue(waste_badge_qs.filter(canteen=small_canteen).exists())
        self.assertTrue(waste_badge_qs.filter(canteen=large_canteen).exists())

    def test_diversification_badge_earned(self):
        """
        Test that the right canteens are identifies in diversification badge qs
        """
        scolaire_sector = SectorFactory(name="Scolaire")

        # --- canteens which don't earn diversification badge:
        high_canteen = CanteenFactory.create()
        high_canteen.sectors.remove(scolaire_sector)
        DiagnosticFactory.create(
            canteen=high_canteen, vegetarian_weekly_recurrence=Diagnostic.MenuFrequency.HIGH.value
        )

        low_canteen = CanteenFactory.create()
        low_canteen.sectors.add(scolaire_sector)
        DiagnosticFactory.create(canteen=low_canteen, vegetarian_weekly_recurrence=Diagnostic.MenuFrequency.LOW.value)

        # --- canteens which earn diversification badge:
        daily_vege = CanteenFactory.create()
        daily_vege.sectors.remove(scolaire_sector)
        DiagnosticFactory.create(canteen=daily_vege, vegetarian_weekly_recurrence=Diagnostic.MenuFrequency.DAILY.value)

        scolaire_mid_vege = CanteenFactory.create()
        scolaire_mid_vege.sectors.add(scolaire_sector)
        DiagnosticFactory.create(
            canteen=scolaire_mid_vege, vegetarian_weekly_recurrence=Diagnostic.MenuFrequency.MID.value
        )

        badges = badges_for_queryset(Diagnostic.objects.all())

        diversification_badge_qs = badges["diversification"]
        self.assertEqual(diversification_badge_qs.count(), 2)
        self.assertTrue(diversification_badge_qs.filter(canteen=daily_vege).exists())
        self.assertTrue(diversification_badge_qs.filter(canteen=scolaire_mid_vege).exists())

    def test_plastic_badge_earned(self):
        """
        Test that the right canteens are identifies in plastic badge qs
        """
        # --- canteens which don't earn
        no_cooking = CanteenFactory.create()
        DiagnosticFactory.create(canteen=no_cooking, cooking_plastic_substituted=False)
        no_serving = CanteenFactory.create()
        DiagnosticFactory.create(canteen=no_serving, serving_plastic_substituted=False)
        no_bottles = CanteenFactory.create()
        DiagnosticFactory.create(canteen=no_bottles, plastic_bottles_substituted=False)
        no_tableware = CanteenFactory.create()
        DiagnosticFactory.create(canteen=no_tableware, plastic_tableware_substituted=False)
        # --- canteens which earn plastic badge:
        earned = CanteenFactory.create()
        DiagnosticFactory.create(
            canteen=earned,
            cooking_plastic_substituted=True,
            serving_plastic_substituted=True,
            plastic_bottles_substituted=True,
            plastic_tableware_substituted=True,
        )

        badges = badges_for_queryset(Diagnostic.objects.all())

        plastic_badge_qs = badges["plastic"]
        self.assertEqual(plastic_badge_qs.count(), 1)
        self.assertTrue(plastic_badge_qs.filter(canteen=earned).exists())

    def test_info_badge_earned(self):
        """
        Test that the right canteens are identified in info badge qs
        """
        no_communicated = CanteenFactory.create()
        DiagnosticFactory.create(canteen=no_communicated, communicates_on_food_quality=False)
        earned = CanteenFactory.create()
        DiagnosticFactory.create(canteen=earned, communicates_on_food_quality=True)

        badges = badges_for_queryset(Diagnostic.objects.all())

        info_badge_qs = badges["info"]
        self.assertEqual(info_badge_qs.count(), 1)
        self.assertTrue(info_badge_qs.filter(canteen=earned).exists())

    def test_canteen_locations(self):
        """
        Test that the right subset of regions and departments 'in use' by canteens are returned
        """
        CanteenFactory.create(department=Department.aisne)
        CanteenFactory.create(department=Department.ain)
        # set region directly
        CanteenFactory.create(region=Region.guadeloupe, department=None)
        # create extra to check that list returned doesn't contain duplicates
        CanteenFactory.create(department=Department.aisne)
        CanteenFactory.create(department="999")  # not a department, checking None on region
        CanteenFactory.create(region="", department="")  # checking exlusion of blank strings

        response = self.client.get(reverse("canteen_locations"))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["regions"]), 3)
        self.assertEqual(Region.guadeloupe, body["regions"][0])
        self.assertEqual(Region.hauts_de_france, body["regions"][1])
        self.assertEqual(Region.auvergne_rhone_alpes, body["regions"][2])
        self.assertEqual(len(body["departments"]), 3)
        self.assertIn(Department.ain, body["departments"][0])
        self.assertIn(Department.aisne, body["departments"][1])
        self.assertIn("999", body["departments"])