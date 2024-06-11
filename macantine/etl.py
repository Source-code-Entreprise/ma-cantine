import pandas as pd
import datetime
import zoneinfo
import logging
import requests
import json
import os
import time
import csv

from abc import ABC, abstractmethod
from data.department_choices import Department
from data.region_choices import Region
from data.models import Canteen, Teledeclaration, Sector
from datetime import date
from api.serializers import SectorSerializer
from api.views.utils import camelize
from django.core.files.storage import default_storage
from django.db.models import Q
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


CAMPAIGN_DATES = {
    2021: {
        "start_date": datetime.datetime(2022, 7, 16, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
        "end_date": datetime.datetime(2022, 12, 5, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
    },
    2022: {
        "start_date": datetime.datetime(2023, 2, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
        "end_date": datetime.datetime(2023, 7, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
    },
    2023: {
        "start_date": datetime.datetime(2024, 1, 8, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
        "end_date": datetime.datetime(2024, 4, 16, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
    },
}

CATEGORIES_TO_AGGREGATE = {
    "bio": ["_bio"],
    "sustainable": ["_sustainable", "_label_rouge", "_aocaop_igp_stg"],
    "egalim_others": [
        "_egalim_others",
        "_hve",
        "_peche_durable",
        "_rup",
        "_fermier",
        "_commerce_equitable",
    ],
    "externality_performance": [
        "_externality_performance",
        "_performance",
        "_externalites",
    ],
}


def map_communes_infos():
    """
    Create a dict that maps cities with their EPCI code
    """
    commune_details = {}
    try:
        logger.info("Starting communes dl")
        response_commune = requests.get("https://geo.api.gouv.fr/communes", timeout=50)
        response_commune.raise_for_status()
        communes = response_commune.json()
        for commune in communes:
            commune_details[commune["code"]] = {}
            if "codeDepartement" in commune.keys():
                commune_details[commune["code"]]["department"] = commune["codeDepartement"]
            if "codeRegion" in commune.keys():
                commune_details[commune["code"]]["region"] = commune["codeRegion"]
            if "codeEpci" in commune.keys():
                commune_details[commune["code"]]["epci"] = commune["codeEpci"]
    except requests.exceptions.HTTPError as e:
        logger.info(e)
        return None
    return commune_details


def map_epcis_code_name():
    try:
        epci_names = {}
        response = requests.get("https://geo.api.gouv.fr/epcis/?fields=nom", timeout=50)
        response.raise_for_status()
        epcis = response.json()
        for epci in epcis:
            epci_names[epci["code"]] = epci["nom"]
        return epci_names
    except requests.exceptions.HTTPError as e:
        logger.info(e)
        return {}


def map_canteens_td(year):
    """
    Populate mapper for a given year. The mapper indicates if one canteen has participated in campaign
    """
    # Check and fetch Teledeclaration data from the database
    tds = Teledeclaration.objects.filter(
        year=year,
        creation_date__range=(
            CAMPAIGN_DATES[year]["start_date"],
            CAMPAIGN_DATES[year]["end_date"],
        ),
        status=Teledeclaration.TeledeclarationStatus.SUBMITTED,
    ).values("canteen_id", "declared_data")

    # Populate the mapper for the given year
    participation = []
    for td in tds:
        participation.append(td["canteen_id"])
        if "satellites" in td["declared_data"]:
            for satellite in td["declared_data"]["satellites"]:
                participation.append(satellite["id"])
    return participation


def map_sectors():
    """
    Populate the details of a sector, given its id
    """
    sectors = Sector.objects.all()
    sectors_mapper = {}
    for sector in sectors:
        sector = camelize(SectorSerializer(sector).data)
        sectors_mapper[sector["id"]] = sector
    return sectors_mapper


def fetch_teledeclarations(years: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for year in years:
        if year in CAMPAIGN_DATES.keys():
            df_year = pd.DataFrame(
                Teledeclaration.objects.filter(
                    year=year,
                    creation_date__range=(
                        CAMPAIGN_DATES[year]["start_date"],
                        CAMPAIGN_DATES[year]["end_date"],
                    ),
                    status=Teledeclaration.TeledeclarationStatus.SUBMITTED,
                    canteen_id__isnull=False,
                ).values()
            )
            df = pd.concat([df, df_year])
        else:
            logger.warning(f"TD dataset does not exist for year : {year}")
        if len(df) == 0:
            logger.warning("TD dataset is empty for all the specified years")
    return df


def flatten_declared_data(df):
    """
    Create a column for each key of the declared_data json column
    """
    df = df.reset_index()
    tmp_df = pd.json_normalize(df["declared_data"])
    df = pd.concat([df.drop("declared_data", axis=1), tmp_df], axis=1)
    return df


def _aggregation_col(df, categ="bio", sub_categ=["_bio"]):
    pattern = "|".join(sub_categ)
    df[f"teledeclaration.value_{categ}_ht"] = df.filter(regex=pattern).sum(
        axis=1, numeric_only=True, skipna=True, min_count=1
    )
    return df


def aggregate_complete_td(df):
    """
    Aggregate the columns of a complete TD for an appro category if the total value of this category is not specified.
    """
    for categ, elements_in_categ in CATEGORIES_TO_AGGREGATE.items():
        df = _aggregation_col(df, categ, elements_in_categ)
    return df


def fetch_commune_detail(code_insee_commune, commune_details, geo_detail_type="epci"):
    """
    Provide EPCI code/ Department code/ Region code for a city, given the insee code of the city
    """
    if (
        code_insee_commune
        and code_insee_commune in commune_details.keys()
        and geo_detail_type in commune_details[code_insee_commune].keys()
    ):
        return commune_details[code_insee_commune][geo_detail_type]
    else:
        return None


def fetch_epci_name(code_insee_epci, epcis_names):
    """
    Provide EPCI code for an epci, given its insee code
    """
    if code_insee_epci and code_insee_epci in epcis_names.keys():
        return epcis_names[code_insee_epci]
    else:
        return None


def format_geo_name(geo_code: int, geo_names: {}):
    """
    Format the name of a region or department from its code
    """
    if isinstance(geo_code, str) and geo_code not in ["978", "987", "975", "988"]:
        geo_name = geo_names[geo_code].split(" - ")[1].lstrip()
        return geo_name
    else:
        return None


def format_sector(sector: dict) -> str:
    return f'""{sector["name"]}""'


def format_list_sectors(sectors) -> str:
    return f'"[{", ".join(sectors)}]"'


def fetch_sector(sector_id, sectors):
    """
    Provide EPCI code for a city, given the insee code of the city
    """
    if sector_id and sector_id in sectors.keys():
        sector = sectors[sector_id]
        return format_sector(sector)
    else:
        return ""


def datetimes_to_str(df):
    date_columns = df.select_dtypes(include=["datetime64[ns, UTC]"]).columns
    for date_column in date_columns:
        df[date_column] = df[date_column].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
    return df


def update_datagouv_resources():
    """
    Updating the URL of the different resources dsiplayed on data.gouv.fr in order to force their cache reload and display the correct update dates
    Returns : Number of updated resources
    """
    if os.environ.get("ENVIRONMENT") != "prod":
        return
    dataset_id = os.getenv("DATAGOUV_DATASET_ID", "")
    api_key = os.getenv("DATAGOUV_API_KEY", "")
    if not (dataset_id and api_key):
        logger.error("Datagouv resource update : API key or dataset id incorrect values")
        return
    header = {"X-API-KEY": api_key}
    try:
        response = requests.get(f"https://www.data.gouv.fr/api/1/datasets/{dataset_id}", headers=header)
        response.raise_for_status()
        resources = response.json()["resources"]
        count_updated_resources = 0
        for resource in resources:
            if resource["format"] in ["xlsx", "csv"]:
                today = date.today()
                updated_url = resource["url"].split("?v=")[0] + "?v=" + today.strftime("%Y%m%d")
                response = requests.put(
                    f'https://www.data.gouv.fr/api/1/datasets/{dataset_id}/resources/{resource["id"]}',
                    headers=header,
                    json={"url": updated_url},
                )
                response.raise_for_status()
                count_updated_resources += 1
        return count_updated_resources
    except requests.HTTPError as e:
        logger.error(f"Datagouv resource update : Error while updating dataset : {dataset_id}")
        logger.exception(e)
    except Exception as e:
        logger.exception(e)


class ETL(ABC):
    """
    Interface for the different ETL
    """

    def __init__(self):
        self.df = None
        self.schema = None
        self.schema_url = ""
        self.dataset_name = ""

    @abstractmethod
    def extract_dataset(self):
        pass

    @abstractmethod
    def transform_dataset(self):
        pass

    @abstractmethod
    def load_dataset(self):
        pass

    def get_dataset(self):
        return self.df

    def len_dataset(self):
        if isinstance(self.df, pd.DataFrame):
            return len(self.df)
        else:
            return 0

    def get_schema(self):
        return self.schema

    def is_valid(self) -> bool:
        dataset_to_validate_url = f"{os.environ['CELLAR_HOST']}/{os.environ['CELLAR_BUCKET_NAME']}/media/open_data/{self.dataset_name}_to_validate.csv"

        res = requests.get(
            f"https://api.validata.etalab.studio/validate?schema={self.schema_url}&url={dataset_to_validate_url}&header_case=true"
        )
        report = json.loads(res.text)["report"]
        if len(report["errors"]) > 0 or report["stats"]["errors"] > 0:
            logger.error(f"The dataset {self.dataset_name} extraction has errors : ")
            logger.error(report["errors"])
            logger.error(report["tasks"])
            return 0
        else:
            return 1


class ETL_OPEN_DATA(ETL):

    def _fill_geo_names(self, geo_zoom="department"):
        """
        Given a dataframe with a column 'department' or 'region', this method maps the name of the location, based on the INSEE code
        Returns:
            pd.Series: The names of the location corresponding to an INSEE code, for each line of the dataset
        """
        if "department" in geo_zoom:
            geo = {i.value: i.label for i in Department}
        elif "region" in geo_zoom:
            geo = {i.value: i.label for i in Region}
        else:
            logger.warning(
                "The desired geo zoom for the method _fill_geo_zoom() is not possible. Please choose between 'department' and 'region'"
            )
            return 0

        self.df[f"{geo_zoom}_lib"] = self.df[geo_zoom].apply(lambda x: format_geo_name(x, geo))

    def transform_geo_data(self, geo_col_names=["department", "region"]):
        logger.info("Start fetching communes details")
        communes_infos = map_communes_infos()

        if "campagne_td" in self.dataset_name:
            # Get department and region as most of TD doesnt have this info
            self.df["canteen_department"] = self.df["canteen_city_insee_code"].apply(
                lambda x: fetch_commune_detail(x, communes_infos, "department")
            )
            self.df["canteen_region"] = self.df["canteen_city_insee_code"].apply(
                lambda x: fetch_commune_detail(x, communes_infos, "region")
            )
            prefix = "canteen_"
        else:
            prefix = ""

        self.df[prefix + "epci"] = self.df[prefix + "city_insee_code"].apply(
            lambda x: fetch_commune_detail(x, communes_infos, "epci")
        )

        epcis_names = map_epcis_code_name()
        self.df[prefix + "epci_lib"] = self.df[prefix + "epci"].apply(lambda x: fetch_epci_name(x, epcis_names))

        for geo in geo_col_names:
            logger.info("Start filling geo_name")
            self._fill_geo_names(geo_zoom=geo)
            col_geo = self.df.pop(f"{geo}_lib")
            self.df.insert(self.df.columns.get_loc(geo) + 1, f"{geo}_lib", col_geo)

    def _clean_dataset(self):
        columns = [i["name"].replace("canteen_", "canteen.") for i in self.schema["fields"]]

        self.df = self.df.loc[:, ~self.df.columns.duplicated()]

        self.df = self.df.reindex(columns, axis="columns")
        self.df.columns = self.df.columns.str.replace(".", "_")
        self.df = self.df.drop_duplicates(subset=["id"])
        self.df = self.df.reset_index(drop=True)

        for col_int in self.schema["fields"]:
            if col_int["type"] == "integer":
                # Force column o Int64 to maintain an integer column despite the NaN values
                self.df[col_int["name"]] = self.df[col_int["name"]].astype("Int64")
            if col_int["type"] == "float":
                self.df[col_int["name"]] = self.df[col_int["name"]].round(decimals=4)
        self.df = self.df.replace("<NA>", "")

    def _extract_sectors(self):
        # Fetching sectors information and aggreting in list in order to have only one row per canteen
        sectors = map_sectors()
        self.df["sectors"] = self.df["sectors"].apply(lambda x: fetch_sector(x, sectors))
        canteens_sectors = self.df.groupby("id")["sectors"].apply(list).apply(format_list_sectors)
        del self.df["sectors"]

        return self.df.merge(canteens_sectors, on="id")

    def load_dataset(self):
        self._load_dataset(stage="to_validate")
        if os.environ["DEFAULT_FILE_STORAGE"] == "storages.backends.s3boto3.S3Boto3Storage":
            logger.info(f"Validating {self.name} dataset. Dataset size : {self.len_dataset()} lines")
            if self.is_valid():
                logger.info(f"Exporting {self.name} dataset to s3")
                self._load_dataset(stage="validated")
            else:
                logger.error(f"The dataset {self.name} is invalid and therefore will not be exported to s3")
        elif os.environ["DEFAULT_FILE_STORAGE"] == "django.core.files.storage.FileSystemStorage":
            logger.info(f"Saving {self.name} dataset locally")
            self._load_dataset(stage="validated")
        else:
            logger.info("Exporting the dataset is not possible with the file system configured")

    def _load_dataset(self, stage="to_validate"):
        if stage == "to_validate":
            filename = f"open_data/{self.dataset_name}_to_validate"
        elif stage == "validated":
            filename = f"open_data/{self.dataset_name}"
        else:
            return 0
        with default_storage.open(filename + ".csv", "w") as file:
            self.df.to_csv(
                file,
                sep=";",
                index=False,
                na_rep="",
                encoding="utf_8_sig",
                quoting=csv.QUOTE_NONE,
            )
        if stage == "validated":
            with default_storage.open(filename + ".parquet", "wb") as file:
                if "sectors" in self.df.columns:
                    self.df.sectors = self.df.sectors.astype(str)
                self.df.to_parquet(file)
            with default_storage.open(filename + ".xlsx", "wb") as file:
                df_export = self.df.copy()
                df_export = datetimes_to_str(df_export)  # Ah Excel !
                df_export.to_excel(file, index=False)
            update_datagouv_resources()


class ETL_CANTEEN(ETL_OPEN_DATA):

    def __init__(self):
        super().__init__()
        self.dataset_name = "registre_cantines"
        self.schema = json.load(open("data/schemas/schema_cantine.json"))
        self.schema_url = (
            "https://raw.githubusercontent.com/betagouv/ma-cantine/staging/data/schemas/schema_cantine.json"
        )
        self.canteens = None

    def extract_dataset(self):
        all_canteens_col = [i["name"] for i in self.schema["fields"]]
        self.canteens_col_from_db = all_canteens_col
        for col_processed in [
            "active_on_ma_cantine",
            "department_lib",
            "region_lib",
            "epci",
            "epci_lib",
            "declaration_donnees_2021",
            "declaration_donnees_2022",
            "declaration_donnees_2023_en_cours",
        ]:
            self.canteens_col_from_db.remove(col_processed)

        exclude_filter = Q(sectors__id=22)  # Filtering out the police / army sectors
        exclude_filter |= Q(deletion_date__isnull=False)  # Filtering out the deleted canteens
        start = time.time()
        self.canteens = Canteen.objects.exclude(exclude_filter)

        if self.canteens.count() == 0:
            return pd.DataFrame(columns=self.canteens_col_from_db)

        # Creating a dataframe with all canteens. The canteens can have multiple lines if they have multiple sectors
        self.df = pd.DataFrame(self.canteens.values(*self.canteens_col_from_db))

        end = time.time()
        logger.info(f"Time spent on canteens extraction : {end - start}")

    def transform_dataset(self):
        # Adding the active_on_ma_cantine column
        start = time.time()
        non_active_canteens = Canteen.objects.filter(managers=None).values_list("id", flat=True)
        end = time.time()
        logger.info(f"Time spent on active canteens : {end - start}")
        self.df["active_on_ma_cantine"] = self.df["id"].apply(lambda x: x not in non_active_canteens)

        logger.info("Canteens : Extract sectors...")
        self.df = self._extract_sectors()

        bucket_url = os.environ.get("CELLAR_HOST")
        bucket_name = os.environ.get("CELLAR_BUCKET_NAME")
        self.df["logo"] = self.df["logo"].apply(lambda x: f"{bucket_url}/{bucket_name}/media/{x}" if x else "")

        logger.info("Canteens : Clean dataset...")
        self._clean_dataset()

        logger.info("Canteens : Fill geo name...")
        start = time.time()
        self.transform_geo_data(geo_col_names=["department", "region"])
        end = time.time()
        logger.info(f"Time spent on geo data : {end - start}")

        logger.info("Canteens : Fill campaign participations...")
        start = time.time()
        for year in [2021, 2022, 2023]:
            campaign_participation = map_canteens_td(year)
            if year == 2023:
                col_name_campaign = f"declaration_donnees_{year}_en_cours"
            else:
                col_name_campaign = f"declaration_donnees_{year}"
            self.df[col_name_campaign] = self.df["id"].apply(lambda x: x in campaign_participation)
        end = time.time()
        logger.info(f"Time spent on campaign participations : {end - start}")


class ETL_TD(ETL_OPEN_DATA):
    def __init__(self, year: int):
        super().__init__()
        self.year = year
        self.dataset_name = f"campagne_td_{year}"
        self.schema = json.load(open("data/schemas/schema_teledeclaration.json"))
        self.schema_url = (
            "https://raw.githubusercontent.com/betagouv/ma-cantine/staging/data/schemas/schema_teledeclaration.json"
        )
        self.df = None

    def extract_dataset(self):
        self.df = fetch_teledeclarations([self.year])

    def transform_sectors(self) -> pd.Series:
        sectors = self.df["canteen_sectors"]
        if not sectors.isnull().all():
            sectors = sectors.apply(lambda x: list(map(lambda y: format_sector(y), x)))
            sectors = sectors.apply(format_list_sectors)
        return sectors

    def transform_dataset(self):
        logger.info("TD campagne : Flatten declared data...")
        self.df = flatten_declared_data(self.df)

        logger.info("TD campagne : Aggregate appro data for complete TD...")
        self.df = aggregate_complete_td(self.df)

        self.df["teledeclaration_ratio_bio"] = (
            self.df["teledeclaration.value_bio_ht"] / self.df["teledeclaration.value_total_ht"]
        )
        self.df["teledeclaration_ratio_egalim_hors_bio"] = (
            self.df["teledeclaration.value_sustainable_ht"] / self.df["teledeclaration.value_total_ht"]
        )

        # Renaming to match schema
        if "teledeclaration.diagnostic_type" in self.df.columns:
            self.df["teledeclaration_type"] = self.df["teledeclaration.diagnostic_type"]
        if "central_kitchen_siret" in self.df.columns:
            self.df["canteen.central_kitchen_siret"] = self.df["central_kitchen_siret"]

        logger.info("TD campagne : Clean dataset...")
        self._clean_dataset()
        logger.info("TD campagne : Filter value total null or value bio null...")
        self._filter_null_values()
        logger.info("TD campagne : Filter by ministry...")
        self._filter_by_ministry()
        logger.info("TD campagne : Filter errors...")
        self._filter_outsiders()
        logger.info("TD campagne : Transform sectors...")
        self.df["canteen_sectors"] = self.transform_sectors()
        logger.info("TD Campagne : Fill geo name...")
        self.transform_geo_data(geo_col_names=["canteen_department", "canteen_region"])

    def _filter_null_values(self):
        "We have decided not take into accounts the TD where the value total or the value bio are null"
        self.df = self.df[~self.df["teledeclaration_ratio_bio"].isnull()]

    def _filter_outsiders(self):
        """
        For the campaign 2023, after analyses, we decided to exclude two TD because their value were impossible
        """
        if self.year == 2022:
            td_with_errors = [9656, 8037]
            self.df = self.df[~self.df["id"].isin(td_with_errors)]

    def _filter_by_ministry(self):
        """
        Filtering the ministry of Armees so they do     not appear publicly
        """
        canteens_to_filter = Canteen.objects.filter(line_ministry="armee")
        canteens_id_to_filter = [canteen.id for canteen in canteens_to_filter]
        self.df = self.df[~self.df["canteen_id"].isin(canteens_id_to_filter)]


class ETL_ANALYSIS(ETL):
    """
    Create a dataset for analysis
    """

    def __init__(self):
        super().__init__()
        self.dataset_name = "analysis"
        self.schema = json.load(open("data/schemas/schema_analysis.json"))
        self.schema_url = (
            "https://raw.githubusercontent.com/betagouv/ma-cantine/staging/data/schemas/schema_analysis.json"
        )
        self.years = [2021, 2022, 2023]

    def extract_dataset(self):
        self.df = fetch_teledeclarations(self.years)

    def transform_dataset(self):
        logger.info("TD campagne : Flatten declared data...")
        self.df = flatten_declared_data(self.df)

        logger.info("TD campagne : Aggregate appro data for complete TD...")
        self.df = aggregate_complete_td(self.df)

        self.df["cuisine_centrale"] = 0
        self.df["modele_economique"] = 0
        self.df["secteur"] = 0
        self.df["catégorie"] = 0
        self.df["value_egalim_ht"] = 0
        self.df["value_externality_ht"] = 0
        self.df["value_fish_france_ht"] = 0
        self.df["lib_departments"] = 0
        self.df["lib_region"] = 0
        self.df["secteur_spe"] = 0
        self.df["ratio_egalim_fish"] = 0
        self.df["ratio_egalim_meat_poultry"] = 0
        self.df["ratio_bio"] = 0
        self.df["ratio_egalim"] = 0

        self._clean_dataset()

    def load_dataset(self):
        """
        Load in database
        """
        try:
            engine = create_engine(
                f"postgresql+psycopg2://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}",
                echo=False,
            )
            self.df.to_sql(name=self.dataset_name, con=engine)
        except Exception as e:
            logger.error("Could not load into database")
            logger.error(e)

    def _clean_dataset(self):
        columns_mapping = {}
        for col in self.df.columns:
            columns_mapping[col] = (
                col.replace("teledeclaration.", "").replace("canteen.", "").replace("applicant.", "")
            )
        self.df = self.df.rename(columns=columns_mapping)

        if "satellites" not in self.df.columns:
            self.df["satellites"] = 0

        self.df = self.df[[i["name"] for i in self.schema["fields"]]]
        self.df = self.df.loc[:, ~self.df.columns.duplicated()]
