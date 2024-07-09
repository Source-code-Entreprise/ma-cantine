import pandas as pd
import requests_mock
from django.test import TestCase
from macantine.etl import map_communes_infos, update_datagouv_resources
from data.factories import DiagnosticFactory, CanteenFactory, UserFactory, SectorFactory
from data.models import Teledeclaration
from macantine.etl import ETL_CANTEEN, ETL_TD, ETL_ANALYSIS
from freezegun import freeze_time
import json
import os


class TestETLAnalysis(TestCase):

    def test_extraction_teledeclaration(self):
        """
        Only teledeclarations that occurred during teledeclaration campaigns should be extracted
        """
        canteen = CanteenFactory.create()
        applicant = UserFactory.create()
        with freeze_time("1991-01-14"):  # Faking time to mock creation_date
            diagnostic_1990 = DiagnosticFactory.create(canteen=canteen, year=1990, diagnostic_type=None)
            _ = Teledeclaration.create_from_diagnostic(diagnostic_1990, applicant)

        with freeze_time("2023-05-14"):  # Faking time to mock creation_date
            diagnostic_2022 = DiagnosticFactory.create(canteen=canteen, year=2022, diagnostic_type=None)
            td_2022 = Teledeclaration.create_from_diagnostic(diagnostic_2022, applicant)

        with freeze_time("2024-02-14"):  # Faking time to mock creation_date
            diagnostic_2023 = DiagnosticFactory.create(canteen=canteen, year=2023, diagnostic_type=None)
            td_2023 = Teledeclaration.create_from_diagnostic(diagnostic_2023, applicant)

        etl_stats = ETL_ANALYSIS()

        etl_stats.extract_dataset()
        self.assertEqual(
            len(etl_stats.df),
            2,
            "There should be two teledeclaration. None for 1990 (no campaign). One for 2022 and one for 2023",
        )
        self.assertEqual(etl_stats.df[etl_stats.df.id == td_2022.id].year[0], 2022)
        self.assertEqual(etl_stats.df[etl_stats.df.id == td_2023.id].year[0], 2023)


@requests_mock.Mocker()
class TestETLOpenData(TestCase):

    @freeze_time("2023-05-14")  # Faking time to mock creation_date
    def test_td_range_years(self, mock):
        """
        Only teledeclarations that occurred during one specific teledeclaration campaign should be extracted
        """
        canteen = CanteenFactory.create()
        applicant = UserFactory.create()
        test_cases = [
            {"name": "Ignore years out of range", "year": 1990, "expected_outcome": 0},
            {"name": "Returns TDs for year in range", "year": 2022, "expected_outcome": 1},
        ]

        for tc in test_cases:
            etl_td = ETL_TD(tc["year"])
            diagnostic = DiagnosticFactory.create(canteen=canteen, year=tc["year"], diagnostic_type=None)
            Teledeclaration.create_from_diagnostic(diagnostic, applicant)
            etl_td.extract_dataset()
            self.assertEqual(etl_td.len_dataset(), tc["expected_outcome"])

    @freeze_time("2023-05-14")  # Faking time to mock creation_date
    def test_ignore_cancelled_tds(self, mock):
        canteen = CanteenFactory.create()
        applicant = UserFactory.create()
        diagnostic = DiagnosticFactory.create(canteen=canteen, year=2022, diagnostic_type=None)
        teledeclaration = Teledeclaration.create_from_diagnostic(diagnostic, applicant)
        teledeclaration.status = Teledeclaration.TeledeclarationStatus.CANCELLED
        teledeclaration.save()

        etl_td = ETL_TD(2022)
        etl_td.extract_dataset()
        self.assertEqual(etl_td.len_dataset(), 0, "The list should be empty as the only td has the CANCELLED status")

    @freeze_time("2023-05-14")  # Faking time to mock creation_date
    def test_transform_teledeclaration(self, mock):

        mock.get(
            "https://geo.api.gouv.fr/communes",
            text=json.dumps(""),
            status_code=200,
        )
        mock.get(
            "https://geo.api.gouv.fr/epcis/?fields=nom",
            text=json.dumps(""),
            status_code=200,
        )

        td = {
            "id": 1,
            "declared_data": {
                "year": 2022,
                "canteen": {
                    "id": 1,
                    "name": "Papa rayon lien.",
                    "siret": None,
                    "region": None,
                    "sectors": [],
                    "department": None,
                    "line_ministry": None,
                    "economic_model": None,
                    "city_insee_code": "68454",
                    "management_type": None,
                    "production_type": None,
                    "daily_meal_count": 8167,
                    "yearly_meal_count": None,
                    "central_producer_siret": None,
                    "satellite_canteens_count": None,
                },
                "version": "10",
                "applicant": {"name": "Lucie Lévêque", "email": "clairemarion@example.net"},
                "teledeclaration": {
                    "id": 1,
                    "year": 2022,
                    "canteen_id": 1,
                    "value_bio_ht": 1537.0,
                    "value_total_ht": 7627.0,
                    "diagnostic_type": None,
                },
                "central_kitchen_siret": None,
            },
            "creation_date": pd.Timestamp("2023-05-14 00:00:00+0000", tz="UTC"),
            "modification_date": pd.Timestamp("2023-05-14 00:00:00+0000", tz="UTC"),
            "year": 2022,
            "canteen_siret": None,
            "status": "SUBMITTED",
            "applicant_id": 3,
            "canteen_id": 1,
            "diagnostic_id": 1,
            "teledeclaration_mode": "SITE",
        }

        schema = json.load(open("data/schemas/schema_teledeclaration.json"))
        schema_cols = [i["name"] for i in schema["fields"]]

        etl_td = ETL_TD(2022)
        etl_td.df = pd.DataFrame.from_dict(td, orient="index").T

        etl_td.transform_dataset()
        self.assertEqual(len(etl_td.get_dataset().columns), len(schema_cols), "The columns should match the schema")

        self.assertEqual(
            etl_td.get_dataset().iloc[0]["canteen_sectors"], '"[]"', "The sectors should be an empty list"
        )

        self.assertGreater(
            etl_td.get_dataset().iloc[0]["teledeclaration_ratio_bio"],
            0,
            "The bio value is aggregated from bio fields and should be greater than 0",
        )

    def test_extraction_canteen(self, mock):
        etl_canteen = ETL_CANTEEN()
        self.assertEqual(etl_canteen.len_dataset(), 0, "There shoud be an empty dataframe")

        # Adding data in the db
        canteen_1 = CanteenFactory.create()
        canteen_1.managers.add(UserFactory.create())

        canteen_2 = CanteenFactory.create()  # Another canteen, but without a manager
        canteen_2.managers.clear()

        etl_canteen.extract_dataset()
        self.assertEqual(len(etl_canteen.df.id.unique()), 2, "There should be two different canteens")

        # Checking the deletion
        canteen_1.delete()
        etl_canteen.extract_dataset()
        self.assertEqual(len(etl_canteen.df.id.unique()), 1, "There should be one canteen less after soft deletion")

        canteen_2.hard_delete()
        etl_canteen = ETL_CANTEEN()
        etl_canteen.extract_dataset()
        self.assertEqual(etl_canteen.len_dataset(), 0, "There should be one canteen less after hard deletion")

    def test_transformation_canteens(self, mock):
        schema = json.load(open("data/schemas/schema_cantine.json"))
        schema_cols = [i["name"] for i in schema["fields"]]

        mock.get(
            "https://geo.api.gouv.fr/communes",
            text=json.dumps([{"code": "29021", "codeEpci": "242900793"}]),
            status_code=200,
        )
        mock.get(
            "https://geo.api.gouv.fr/epcis/?fields=nom",
            text=json.dumps([{"nom": "CC Communauté Lesneven Côte des Légendes", "code": "242900793"}]),
            status_code=200,
        )

        canteens_data = {
            "0": {
                "id": 1,
                "name": "Dimanche regretter.",
                "siret": None,
                "city": None,
                "city_insee_code": "29021",
                "postal_code": None,
                "department": None,
                "region": None,
                "sectors": None,
            },
            "1": {
                "id": 2,
                "name": "Jazz",
                "siret": None,
                "city": "Dias",
                "city_insee_code": "29859",
                "postal_code": None,
                "department": None,
                "region": None,
                "sectors": None,
            },
        }
        etl_canteen = ETL_CANTEEN()
        etl_canteen.df = pd.DataFrame.from_dict(canteens_data, orient="index")

        etl_canteen.transform_dataset()
        canteens = etl_canteen.get_dataset()

        # Check the schema matching
        self.assertEqual(len(canteens.columns), len(schema_cols), "The columns should match the schema.")

        # Checking that the geo data has been fetched from the city insee code
        self.assertEqual(canteens[canteens.id == canteens_data["0"]["id"]].iloc[0]["epci"], "242900793")

        # Check that the names of the region and departments are fetched from the code
        self.assertEqual(
            canteens[canteens.id == canteens_data["0"]["id"]].iloc[0]["epci_lib"],
            "CC Communauté Lesneven Côte des Légendes",
        )

    def test_active_on_ma_cantine(self, mock):
        mock.get(
            "https://geo.api.gouv.fr/communes",
            text=json.dumps(""),
            status_code=200,
        )
        mock.get(
            "https://geo.api.gouv.fr/epcis/?fields=nom",
            text=json.dumps(""),
            status_code=200,
        )

        # Adding data in the db
        canteen_1 = CanteenFactory.create()
        canteen_1.managers.add(UserFactory.create())
        canteen_2 = CanteenFactory.create()
        canteen_2.managers.clear()

        etl_canteen = ETL_CANTEEN()
        etl_canteen.extract_dataset()
        etl_canteen.transform_dataset()
        canteens = etl_canteen.get_dataset()

        self.assertTrue(
            canteens[canteens.id == canteen_1.id].iloc[0]["active_on_ma_cantine"],
            "The canteen should be active because there is at least one manager",
        )
        self.assertFalse(
            canteens[canteens.id == canteen_2.id].iloc[0]["active_on_ma_cantine"],
            "The canteen should not be active because there no manager",
        )

    @freeze_time("2023-05-14")  # Faking time to mock creation_date
    def test_campaign_participation(self, mock):
        mock.get(
            "https://geo.api.gouv.fr/communes",
            text=json.dumps(""),
            status_code=200,
        )
        mock.get(
            "https://geo.api.gouv.fr/epcis/?fields=nom",
            text=json.dumps(""),
            status_code=200,
        )
        etl_canteen = ETL_CANTEEN()

        canteen_td = CanteenFactory.create()
        _ = CanteenFactory.create()
        applicant = UserFactory.create()
        diagnostic_2022 = DiagnosticFactory.create(canteen=canteen_td, year=2022, diagnostic_type=None)
        _ = Teledeclaration.create_from_diagnostic(diagnostic_2022, applicant)
        etl_canteen.extract_dataset()
        etl_canteen.transform_dataset()
        canteens = etl_canteen.get_dataset()
        self.assertEqual(
            canteens[canteens.id == canteen_td.id].iloc[0]["declaration_donnees_2022"],
            True,
            "The canteen has participated in the campain",
        )
        self.assertEqual(
            canteens[canteens.id != canteen_td.id].iloc[0]["declaration_donnees_2022"],
            False,
            "The canteen hasn't participated in the campain",
        )

    def test_transformation_canteens_sectors(self, mock):
        mock.get(
            "https://geo.api.gouv.fr/communes",
            text=json.dumps(""),
            status_code=200,
        )
        mock.get(
            "https://geo.api.gouv.fr/epcis/?fields=nom",
            text=json.dumps(""),
            status_code=200,
        )

        etl_canteen = ETL_CANTEEN()

        # Adding data in the db
        canteen = CanteenFactory(sectors=[])
        canteen.sectors.clear()

        etl_canteen.extract_dataset()

        try:
            etl_canteen.transform_dataset()
        except Exception:
            self.fail(
                "The extraction should not fail if one column is completely empty. In this case, there is no sector"
            )
        canteens = etl_canteen.get_dataset()
        self.assertEqual(
            canteens[canteens.id == canteen.id].iloc[0]["sectors"], '"[]"', "The sectors should be an empty list"
        )

        # Testing the filtering of canteens from sector 22
        len_dataset_without_sector_22 = len(canteens)
        CanteenFactory.create(sectors=[SectorFactory.create(id=22)])
        etl_canteen.extract_dataset()
        etl_canteen.transform_dataset()
        canteens = etl_canteen.get_dataset()
        self.assertEqual(
            len_dataset_without_sector_22,
            len(canteens),
            "The new canteen should not appear as its specific sector has to remain private",
        )

    def test_map_communes_infos(self, mock):
        mock.get(
            "https://geo.api.gouv.fr/communes",
            text=json.dumps(
                [
                    {
                        "nom": "L'Abergement-Clémenciat",
                        "code": "01001",
                        "codeDepartement": "01",
                        "siren": "210100012",
                        "codeEpci": "200069193",
                        "codeRegion": "84",
                        "codesPostaux": ["01400"],
                        "population": "832",
                    },
                    {
                        "nom": "L'Abergement-de-Varey",
                        "code": "01002",
                        "codeDepartement": "01",
                        "siren": "210100020",
                        "codeRegion": "84",
                        "codesPostaux": ["01640"],
                        "population": "267",
                    },
                ]
            ),
        )

        communes_details = map_communes_infos()
        self.assertEqual(len(communes_details), 2)
        self.assertCountEqual(list(communes_details.keys()), ["01001", "01002"])
        self.assertEqual(communes_details["01001"]["department"], "01")
        self.assertEqual(communes_details["01001"]["region"], "84")
        self.assertEqual(communes_details["01001"]["epci"], "200069193")

        self.assertNotIn("epci", communes_details["01002"].keys(), "Not all cities are part of an EPCI")

    @freeze_time("2023-05-14")  # Faking date to check new url
    def test_update_ressource(self, mock):
        dataset_id = "expected_dataset_id"
        os.environ["DATAGOUV_DATASET_ID"] = dataset_id

        api_key = "expected_api_key"
        os.environ["DATAGOUV_API_KEY"] = api_key
        expected_header = {"X-API-KEY": api_key}

        ressource_id = "expected_resource_id"

        mock.get(
            f"https://www.data.gouv.fr/api/1/datasets/{dataset_id}",
            headers=expected_header,
            json={
                "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again. You have requested this URI [/api/1/datasets/6482def590d4cf8cea/] but did you mean /api/1/datasets/schemas/ or /api/1/datasets/<dataset:dataset>/featured/ or /api/1/datasets/<dataset:dataset>/resources/<uuid:rid>/ ?"
            },
            status_code=404,
        )

        os.environ["ENVIRONMENT"] = "prod"
        number_of_updated_resources = update_datagouv_resources()
        self.assertIsNone(number_of_updated_resources)

        mock.get(
            f"https://www.data.gouv.fr/api/1/datasets/{dataset_id}",
            headers=expected_header,
            text=json.dumps(
                {
                    "resources": [
                        {
                            "id": "a_resource_id",
                            "format": "wrong_format",
                            "url": "https://my-url.org/fichier.txt?v=old_date",
                        },
                        {
                            "id": "expected_resource_id",
                            "format": "csv",
                            "url": "https://my-url.org/fichier.csv?v=old_date",
                        },
                    ]
                }
            ),
            status_code=200,
        )
        mock.put(
            f"https://www.data.gouv.fr/api/1/datasets/{dataset_id}/resources/{ressource_id}",
            headers=expected_header,
            json={
                "url": "https://cellar-c2.services.clever-cloud.com/ma-cantine-egalim-prod/media/open_data/registre_cantines.xlsx?v=230514"
            },
            status_code=200,
        )

        os.environ["ENVIRONMENT"] = "not-prod"
        number_of_updated_resources = update_datagouv_resources()
        self.assertIsNone(
            number_of_updated_resources, "No resource should be updated as the environment is not production"
        )

        os.environ["ENVIRONMENT"] = "prod"
        number_of_updated_resources = update_datagouv_resources()
        self.assertEqual(number_of_updated_resources, 1, "Only the csv resource should be updated")
