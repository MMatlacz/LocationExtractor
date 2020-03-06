import os
import re
from typing import List, Set, Tuple, Optional

import pandas as pd

from location_extractor import src_dir
from location_extractor.containers import Country, Region, City
from location_extractor.helpers import capitalize_name, remove_accents
from location_extractor.named_entity_recognition.ner import NERExtractor
from location_extractor.utils import fuzzy_match


class Extractor:
    def __init__(self):
        self.extractor = NERExtractor()
        locations_path = os.path.join(
            src_dir, "data", "GeoLite2-City-CSV_20200303", "GeoLite2-City-Locations-en-processed.csv")
        self.locations_data = pd.read_csv(locations_path)

    def is_a_country(self, name: str) -> bool:
        name_clean = remove_accents(capitalize_name(name))
        query = f"country_name == @name_clean"
        countries_df = self.locations_data.query(query)
        return not countries_df.empty

    def places_by_name(self, place_name, column_name) -> pd.DataFrame:
        capitalized_name = remove_accents(capitalize_name(place_name))
        query = f"{column_name} == @place_name"
        rows = self.locations_data.query(query)
        if not rows.empty:
            return rows

        return rows

    def cities_for_name(self, city_name: str) -> Optional[pd.DataFrame]:
        return self.places_by_name(city_name, 'city_name')

    def regions_for_name(self, region_name: str) -> Optional[pd.DataFrame]:
        return self.places_by_name(region_name, 'subdivision_name')

    def resolve_acronyms(self, place: str) -> str:
        name = re.sub(
            r"(^|(?P<before>\S*)\s)(?:The\s+)?(?P<country>usa)($|\s(?P<after>\S*))",
            r"\g<before> United States \g<after>",
            place,
            flags=re.IGNORECASE
        )
        name = re.sub(
            r"(^|(?P<before>\S*)\s)(?:The\s+)?(?P<country>uk)($|\s(?P<after>\S*))",
            r"\g<before> United Kingdom \g<after>",
            name,
            flags=re.IGNORECASE
        )
        return name.strip()

    def get_countries(self, places: List[str]) -> Tuple[List[Country], Set[str]]:
        countries = []
        remaining_places = set()
        for i, original in enumerate(places):
            resolved = self.resolve_acronyms(original)
            name_clean = remove_accents(capitalize_name(resolved))
            query = f"country_name == '{name_clean}'"
            countries_df = self.locations_data.query(query)

            if not countries_df.empty:
                for _, row in countries_df.iterrows():
                    country_name = row['country_name']
                    iso_code = row['country_iso_code']
                    country = Country(name=country_name, iso_code=iso_code)
                    if country not in countries:
                        countries.append(country)
            else:
                remaining_places.add(original)

        return countries, remaining_places

    def get_regions(self, places: Set[str], countries: List[Country]) -> Tuple[List[Region], Set[str]]:
        found_regions = []
        remaining_places = set()

        for place in places:
            for country in countries:
                name_clean = remove_accents(capitalize_name(country.name))
                query = f"country_name == '{name_clean}'"
                regions_df = self.locations_data.query(query)

                for region in regions_df['subdivision_name'].unique():
                    if fuzzy_match(place, region):
                        if region not in found_regions:
                            found_regions.append(region)
                    else:
                        remaining_places.add(place)
            else:
                remaining_places.add(place)

        return found_regions, remaining_places

    def get_cities(self,
                   places: Set[str], countries: List[Country], regions: List[Region]) -> Tuple[List[City], Set[str]]:
        remaining_places = set()
        cities = []
        for place in places:
            iso_codes = [country.iso_code for country in countries]

            query = f'city_name == "{capitalize_name(remove_accents(place))}"'
            cities_df = self.locations_data.query(query)

            found_cities = []
            cities_in_countries = cities_df[cities_df.country_iso_code.isin(iso_codes)].copy()
            cities_df = cities_df[~cities_df.city_name.isin(cities_in_countries.city_name.unique())]

            for i, row in pd.concat([cities_in_countries, cities_df], axis=0).iterrows():
                city_name = row.city_name
                region_name = row.subdivision_name

                country = Country(name=row.country_name, iso_code=row.country_iso_code)
                if country not in countries:
                    countries.append(country)

                if bool(countries) == bool(country in countries):
                    region = Region(name=region_name, country=country)
                    regions.append(region)
                else:
                    region = None

                if bool(regions) == bool(region in regions):
                    city = City(name=city_name, region=region, country=country)
                else:
                    city = None

                if city and city not in cities:
                    found_cities.append(city)

            if found_cities:
                cities += found_cities
            else:
                remaining_places.add(place)

        return cities, remaining_places

    def extract_locations(self, text=None):
        places = self.extractor.find_entities(text)

        countries, remaining_places = self.get_countries(places)
        regions, remaining_places = self.get_regions(remaining_places, countries)
        cities, remaining_places = self.get_cities(remaining_places, countries, regions)

        return countries, regions, cities, remaining_places

    def is_location(self, place: str) -> bool:
        countries, remaining_places = self.get_countries([place])
        regions, remaining_places = self.get_regions(remaining_places, countries)
        cities, remaining_places = self.get_cities(remaining_places, countries, regions)

        if cities or regions or countries:
            return True
        else:
            return False
