import os
import datetime
from datetime import date
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from data.factories import CanteenFactory, SectorFactory
from data.factories import DiagnosticFactory
from data.models import Canteen
from data.region_choices import Region

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TestPublicCanteenPreviewsApi(APITestCase):
    def test_get_published_canteens(self):
        """
        Only published canteens with public data should be
        returned from this call
        """
        published_canteens = [
            CanteenFactory.create(publication_status=Canteen.PublicationStatus.PUBLISHED.value),
            CanteenFactory.create(publication_status=Canteen.PublicationStatus.PUBLISHED.value),
        ]
        private_canteens = [
            CanteenFactory.create(),
            CanteenFactory.create(publication_status=Canteen.PublicationStatus.DRAFT.value),
        ]
        response = self.client.get(reverse("published_canteens"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        body = response.json()
        self.assertEqual(body.get("count"), 2)

        results = body.get("results", [])

        for published_canteen in published_canteens:
            self.assertTrue(any(x["id"] == published_canteen.id for x in results))

        for private_canteen in private_canteens:
            self.assertFalse(any(x["id"] == private_canteen.id for x in results))

        for recieved_canteen in results:
            self.assertFalse("managers" in recieved_canteen)
            self.assertFalse("managerInvitations" in recieved_canteen)


class TestPublicCanteenSearchApi(APITestCase):
    def test_search_single_result(self):
        CanteenFactory.create(publication_status="published", name="Shiso")
        CanteenFactory.create(publication_status="published", name="Wasabi")
        CanteenFactory.create(publication_status="published", name="Mochi")
        CanteenFactory.create(publication_status="published", name="Umami")

        search_term = "mochi"
        response = self.client.get(f"{reverse('published_canteens')}?search={search_term}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results", [])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("name"), "Mochi")

    def test_search_accented_result(self):
        CanteenFactory.create(publication_status="published", name="Wakamé")
        CanteenFactory.create(publication_status="published", name="Shiitaké")

        search_term = "wakame"
        response = self.client.get(f"{reverse('published_canteens')}?search={search_term}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results", [])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("name"), "Wakamé")

    def test_search_multiple_results(self):
        CanteenFactory.create(publication_status="published", name="Sudachi")
        CanteenFactory.create(publication_status="published", name="Wasabi")
        CanteenFactory.create(publication_status="published", name="Mochi")
        CanteenFactory.create(publication_status="published", name="Umami")

        search_term = "chi"
        response = self.client.get(f"{reverse('published_canteens')}?search={search_term}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results", [])

        self.assertEqual(len(results), 2)

        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Mochi", result_names)
        self.assertIn("Sudachi", result_names)

    def test_meal_count_filter(self):
        CanteenFactory.create(publication_status="published", daily_meal_count=10, name="Shiso")
        CanteenFactory.create(publication_status="published", daily_meal_count=15, name="Wasabi")
        CanteenFactory.create(publication_status="published", daily_meal_count=20, name="Mochi")
        CanteenFactory.create(publication_status="published", daily_meal_count=25, name="Umami")

        # Only "Shiso" is between 9 and 11 meal count
        min_meal_count = 9
        max_meal_count = 11
        query_params = f"min_daily_meal_count={min_meal_count}&max_daily_meal_count={max_meal_count}"
        url = f"{reverse('published_canteens')}?{query_params}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("name"), "Shiso")

        # "Shiso" and "Wasabi" are between 9 and 15 meal count
        min_meal_count = 9
        max_meal_count = 15
        query_params = f"min_daily_meal_count={min_meal_count}&max_daily_meal_count={max_meal_count}"
        url = f"{reverse('published_canteens')}?{query_params}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 2)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)
        self.assertIn("Wasabi", result_names)

        # No canteen has less than 5 meal count
        max_meal_count = 5
        query_params = f"max_daily_meal_count={max_meal_count}"
        url = f"{reverse('published_canteens')}?{query_params}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 0)

        # Filters are inclusive, so a value of 25 brings "Umami"
        min_meal_count = 25
        query_params = f"min_daily_meal_count={min_meal_count}"
        url = f"{reverse('published_canteens')}?{query_params}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("name"), "Umami")

    def test_department_filter(self):
        CanteenFactory.create(publication_status="published", department="69", name="Shiso")
        CanteenFactory.create(publication_status="published", department="10", name="Wasabi")
        CanteenFactory.create(publication_status="published", department="75", name="Mochi")
        CanteenFactory.create(publication_status="published", department="31", name="Umami")

        url = f"{reverse('published_canteens')}?department=69"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("name"), "Shiso")

    def test_sectors_filter(self):
        school = SectorFactory.create(name="School")
        enterprise = SectorFactory.create(name="Enterprise")
        social = SectorFactory.create(name="Social")
        CanteenFactory.create(publication_status="published", sectors=[school], name="Shiso")
        CanteenFactory.create(publication_status="published", sectors=[enterprise], name="Wasabi")
        CanteenFactory.create(publication_status="published", sectors=[social], name="Mochi")
        CanteenFactory.create(publication_status="published", sectors=[school, social], name="Umami")

        url = f"{reverse('published_canteens')}?sectors={school.id}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 2)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)
        self.assertIn("Umami", result_names)

        url = f"{reverse('published_canteens')}?sectors={enterprise.id}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("name"), "Wasabi")

        url = f"{reverse('published_canteens')}?sectors={enterprise.id}&sectors={social.id}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 3)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Wasabi", result_names)
        self.assertIn("Mochi", result_names)
        self.assertIn("Umami", result_names)

    def test_order_search(self):
        """
        By default, list canteens by creation date descending
        Optionally sort by name, modification date, number of meals
        """
        CanteenFactory.create(
            publication_status="published",
            daily_meal_count=200,
            name="Shiso",
            creation_date=(timezone.now() - datetime.timedelta(days=10)),
        )
        CanteenFactory.create(
            publication_status="published",
            daily_meal_count=100,
            name="Wasabi",
            creation_date=(timezone.now() - datetime.timedelta(days=8)),
        )
        last_modified = CanteenFactory.create(
            publication_status="published",
            daily_meal_count=300,
            name="Mochi",
            creation_date=(timezone.now() - datetime.timedelta(days=6)),
        )
        CanteenFactory.create(
            publication_status="published",
            daily_meal_count=150,
            name="Umami",
            creation_date=(timezone.now() - datetime.timedelta(days=4)),
        )

        url = f"{reverse('published_canteens')}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "Umami")
        self.assertEqual(results[1]["name"], "Mochi")
        self.assertEqual(results[2]["name"], "Wasabi")
        self.assertEqual(results[3]["name"], "Shiso")

        url = f"{reverse('published_canteens')}?ordering=name"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "Mochi")
        self.assertEqual(results[1]["name"], "Shiso")
        self.assertEqual(results[2]["name"], "Umami")
        self.assertEqual(results[3]["name"], "Wasabi")

        last_modified.daily_meal_count = 900
        last_modified.save()

        url = f"{reverse('published_canteens')}?ordering=-modification_date"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "Mochi")
        self.assertEqual(results[1]["name"], "Umami")
        self.assertEqual(results[2]["name"], "Wasabi")
        self.assertEqual(results[3]["name"], "Shiso")

        url = f"{reverse('published_canteens')}?ordering=daily_meal_count"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "Wasabi")
        self.assertEqual(results[1]["name"], "Umami")
        self.assertEqual(results[2]["name"], "Shiso")
        self.assertEqual(results[3]["name"], "Mochi")

    def test_order_meal_count(self):
        """
        In meal count, "null" values should be placed first
        """
        CanteenFactory.create(
            publication_status="published",
            daily_meal_count=None,
            name="Shiso",
            creation_date=(timezone.now() - datetime.timedelta(days=10)),
        )
        CanteenFactory.create(
            publication_status="published",
            daily_meal_count=0,
            name="Wasabi",
            creation_date=(timezone.now() - datetime.timedelta(days=8)),
        )
        CanteenFactory.create(
            publication_status="published",
            daily_meal_count=1,
            name="Mochi",
            creation_date=(timezone.now() - datetime.timedelta(days=6)),
        )
        CanteenFactory.create(
            publication_status="published",
            daily_meal_count=2,
            name="Umami",
            creation_date=(timezone.now() - datetime.timedelta(days=4)),
        )

        url = f"{reverse('published_canteens')}?ordering=daily_meal_count"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "Shiso")
        self.assertEqual(results[1]["name"], "Wasabi")
        self.assertEqual(results[2]["name"], "Mochi")
        self.assertEqual(results[3]["name"], "Umami")

        url = f"{reverse('published_canteens')}?ordering=-daily_meal_count"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["name"], "Umami")
        self.assertEqual(results[1]["name"], "Mochi")
        self.assertEqual(results[2]["name"], "Wasabi")
        self.assertEqual(results[3]["name"], "Shiso")

    def test_filter_appro_values(self):
        """
        Should be able to filter by bio %, sustainable %, combined % based on last year's diagnostic
        """
        good_canteen = CanteenFactory.create(
            publication_status="published", name="Shiso", region=Region.auvergne_rhone_alpes
        )
        medium_canteen = CanteenFactory.create(
            publication_status="published", name="Wasabi", region=Region.auvergne_rhone_alpes
        )
        sustainable_canteen = CanteenFactory.create(
            publication_status="published", name="Umami", region=Region.auvergne_rhone_alpes
        )
        bad_canteen = CanteenFactory.create(
            publication_status="published", name="Mochi", region=Region.auvergne_rhone_alpes
        )
        secretly_good_canteen = CanteenFactory.create(
            publication_status="draft", name="Secret", region=Region.auvergne_rhone_alpes
        )
        guadeloupe_canteen = CanteenFactory.create(
            publication_status=Canteen.PublicationStatus.PUBLISHED, region=Region.guadeloupe, name="Guadeloupe"
        )

        publication_year = date.today().year - 1
        DiagnosticFactory.create(
            canteen=good_canteen,
            year=publication_year,
            value_total_ht=100,
            value_bio_ht=30,
            value_sustainable_ht=10,
            value_externality_performance_ht=10,
            value_egalim_others_ht=10,
        )
        DiagnosticFactory.create(
            canteen=secretly_good_canteen,
            year=publication_year,
            value_total_ht=100,
            value_bio_ht=30,
            value_sustainable_ht=30,
            value_externality_performance_ht=0,
            value_egalim_others_ht=0,
        )
        DiagnosticFactory.create(
            canteen=medium_canteen,
            year=publication_year,
            value_total_ht=1000,
            value_bio_ht=150,
            value_sustainable_ht=350,
            value_externality_performance_ht=None,
            value_egalim_others_ht=None,
        )
        DiagnosticFactory.create(
            canteen=sustainable_canteen,
            year=publication_year,
            value_total_ht=100,
            value_bio_ht=None,
            value_sustainable_ht=None,
            value_externality_performance_ht=40,
            value_egalim_others_ht=20,
        )
        DiagnosticFactory.create(
            canteen=bad_canteen,
            year=2019,
            value_total_ht=100,
            value_bio_ht=30,
            value_sustainable_ht=30,
            value_externality_performance_ht=0,
            value_egalim_others_ht=0,
        )
        DiagnosticFactory.create(
            canteen=bad_canteen,
            year=publication_year,
            value_total_ht=10,
            value_bio_ht=0,
            value_sustainable_ht=0,
            value_externality_performance_ht=0,
            value_egalim_others_ht=0,
        )
        DiagnosticFactory.create(
            canteen=guadeloupe_canteen,
            year=publication_year,
            value_total_ht=100,
            value_bio_ht=5,
            value_sustainable_ht=15,
            value_externality_performance_ht=None,
            value_egalim_others_ht=0,
        )
        url = f"{reverse('published_canteens')}?min_portion_bio={0.2}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 1)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)

        url = f"{reverse('published_canteens')}?min_portion_combined={0.5}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 3)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)
        self.assertIn("Wasabi", result_names)
        self.assertIn("Umami", result_names)

        url = f"{reverse('published_canteens')}?min_portion_bio={0.1}&min_portion_combined={0.5}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 2)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)
        self.assertIn("Wasabi", result_names)

        url = f"{reverse('published_canteens')}?badge=appro"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 2)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)
        self.assertIn("Guadeloupe", result_names)

        # if both badge and thresholds specified, return the results that match the most strict threshold
        url = f"{reverse('published_canteens')}?badge=appro&min_portion_combined={0.01}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 2)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)
        self.assertIn("Guadeloupe", result_names)

        url = f"{reverse('published_canteens')}?badge=appro&min_portion_combined={0.5}"
        response = self.client.get(url)
        results = response.json().get("results", [])
        self.assertEqual(len(results), 1)
        result_names = list(map(lambda x: x.get("name"), results))
        self.assertIn("Shiso", result_names)

    def test_pagination_departments(self):
        CanteenFactory.create(publication_status="published", department="75", name="Shiso")
        CanteenFactory.create(publication_status="published", department="75", name="Wasabi")
        CanteenFactory.create(publication_status="published", department="69", name="Mochi")
        CanteenFactory.create(publication_status="published", department=None, name="Umami")

        url = f"{reverse('published_canteens')}"
        response = self.client.get(url)
        body = response.json()

        # There are two unique departments : 75 and 69
        self.assertEqual(len(body.get("departments")), 2)
        self.assertIn("75", body.get("departments"))
        self.assertIn("69", body.get("departments"))

    def test_pagination_sectors(self):
        """
        The pagination endpoint should return all sectors that are used by canteens, even when the data is filtered by another sector
        """
        school = SectorFactory.create(name="School")
        enterprise = SectorFactory.create(name="Enterprise")
        administration = SectorFactory.create(name="Administration")
        # unused sectors shouldn't show up as an option
        SectorFactory.create(name="Unused")
        CanteenFactory.create(publication_status="published", sectors=[school, enterprise], name="Shiso")
        CanteenFactory.create(publication_status="published", sectors=[school], name="Wasabi")
        CanteenFactory.create(publication_status="published", sectors=[school], name="Mochi")
        CanteenFactory.create(publication_status="published", sectors=[administration], name="Umami")

        url = f"{reverse('published_canteens')}"
        response = self.client.get(url)
        body = response.json()

        self.assertEqual(len(body.get("sectors")), 3)
        self.assertIn(school.id, body.get("sectors"))
        self.assertIn(enterprise.id, body.get("sectors"))
        self.assertIn(administration.id, body.get("sectors"))

        url = f"{reverse('published_canteens')}?sectors={enterprise.id}"
        response = self.client.get(url)
        body = response.json()

        self.assertEqual(len(body.get("sectors")), 3)
        self.assertIn(school.id, body.get("sectors"))
        self.assertIn(enterprise.id, body.get("sectors"))
        self.assertIn(administration.id, body.get("sectors"))

    def test_pagination_management_types(self):
        CanteenFactory.create(publication_status="published", management_type="conceded", name="Shiso")
        CanteenFactory.create(publication_status="published", management_type=None, name="Wasabi")

        url = f"{reverse('published_canteens')}"
        response = self.client.get(url)
        body = response.json()

        self.assertEqual(len(body.get("managementTypes")), 1)
        self.assertIn("conceded", body.get("managementTypes"))

    def test_get_canteens_filter_production_type(self):
        site_canteen = CanteenFactory.create(publication_status="published", production_type="site")
        central_cuisine = CanteenFactory.create(publication_status="published", production_type="central")
        central_serving_cuisine = CanteenFactory.create(
            publication_status="published", production_type="central_serving"
        )

        response = self.client.get(f"{reverse('published_canteens')}?production_type=central,central_serving")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()

        self.assertEqual(body["count"], 2)
        ids = list(map(lambda x: x["id"], body["results"]))
        self.assertIn(central_cuisine.id, ids)
        self.assertIn(central_serving_cuisine.id, ids)
        self.assertNotIn(site_canteen.id, ids)
