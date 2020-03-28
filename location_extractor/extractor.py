import os
import re
from typing import List, Set, Tuple, Optional

import pandas as pd

from location_extractor import src_dir
from location_extractor.containers import Country, Region, City, Continent
from location_extractor.helpers import remove_accents, parse_query_param
from location_extractor.named_entity_recognition.ner import NERExtractor


class Extractor:
    sublocation_pattern = re.compile(
        r"\s*(west|south|north|east)(ern)?\s*",
        re.IGNORECASE
    )
    clean_acronym_pattern = re.compile(
        r"(^|\s)(the)(\s|$)", flags=re.IGNORECASE
    )

    def __init__(self) -> None:
        self.extractor = NERExtractor()
        locations_path = os.path.join(
            src_dir, "data", "GeoLite2-City-CSV_20200303", "GeoLite2-City-Locations-en-processed.csv")
        self.locations_data: pd.DataFrame = pd.read_csv(locations_path)

        for col in self.locations_data.select_dtypes(include=['object', 'string']):
            self.locations_data[f'{col}_lowercase'] = self.locations_data[col].str.lower()

        self.acronyms_mapping = {
            "UK": "United Kingdom",
            "USA": "United States",
        }

    def build_query(self, column: str, value: str):
        return f"{column}_lowercase == '{parse_query_param(value)}'"

    def places_by_name(self, place_name, column_name) -> Optional[pd.DataFrame]:
        query = self.build_query(column_name, place_name)
        rows = self.locations_data.query(query)
        return rows if not rows.empty else None

    def cities_for_name(self, city_name: str) -> Optional[pd.DataFrame]:
        return self.places_by_name(city_name, 'city_name')

    def regions_for_name(self, region_name: str) -> Optional[pd.DataFrame]:
        return self.places_by_name(region_name, 'subdivision_name')

    def get_continents(self, places) -> Tuple[List[Continent], Set[str]]:
        continents = set()
        remaining_places = set()
        for place in places:
            continent_query = self.build_query('continent_name', place)
            continents_df = self.locations_data.query(continent_query)

            potential_continents = Continent.from_dicts(continents_df.to_dict("records"))

            if potential_continents:
                continents = continents.union(potential_continents)
            else:
                remaining_places.add(place)

        return list(continents), remaining_places

    def get_countries(self, places: List[str], continents: List[Continent]) -> Tuple[List[Country], Set[str]]:
        countries = set()
        remaining_places = set()
        for place in places:
            resolved = self.resolve_acronym(place)

            country_query = self.build_query('country_name', resolved or place)
            countries_df = self.locations_data.query(country_query)

            potential_countries = Country.from_dicts(countries_df.to_dict("records"))

            countries_on_continents = [country for country in potential_countries if country.continent in continents]

            if countries_on_continents:
                countries = countries.union(countries_on_continents)
            elif potential_countries:
                countries = countries.union(potential_countries)
            else:
                remaining_places.add(place)

        return list(countries), remaining_places

    def get_regions(self, places: Set[str], continents: List[Continent],
                    countries: List[Country]) -> Tuple[List[Region], Set[str]]:
        regions = set()
        remaining_places = set()

        for place in places:
            subdivision_query = self.build_query('subdivision_name', place)
            regions_df = self.locations_data.query(subdivision_query)

            potential_regions = Region.from_dicts(regions_df.to_dict("records"))

            regions_in_country = [region for region in potential_regions if region.country in countries]
            regions_on_continents = [region for region in potential_regions if region.country.continent in continents]

            if regions_in_country:
                regions = regions.union(regions_in_country)
            elif regions_on_continents:
                regions = regions.union(regions_on_continents)
            elif potential_regions:
                regions = regions.union(potential_regions)
            else:
                remaining_places.add(place)

        return list(regions), remaining_places

    def get_cities(self, places: Set[str], continents: List[Continent], countries: List[Country],
                   regions: List[Region]) -> Tuple[List[City], Set[str]]:
        remaining_places = set()
        cities = set()
        for place in places:
            city_query = self.build_query('city_name', place)

            cities_df = self.locations_data.query(city_query)
            potential_cities = City.from_dicts(cities_df.to_dict("records"))

            cities_in_regions = [city for city in potential_cities if city.region in regions]
            cities_in_country = [city for city in potential_cities if city.country in countries]
            cities_on_continents = [city for city in potential_cities if city.country.continent in continents]

            if cities_in_regions:
                cities = cities.union(cities_in_regions)
            elif cities_in_country:
                cities = cities.union(cities_in_country)
            elif cities_on_continents:
                cities = cities.union(cities_on_continents)
            elif potential_cities:
                cities = cities.union(potential_cities)
            else:
                remaining_places.add(place)

        return list(cities), remaining_places

    def resolve_acronym(self, name) -> Optional[str]:
        name_clean = remove_accents(name)
        name_clean = self.clean_acronym_pattern.sub("", name_clean)
        name_upper = name_clean.upper()
        resolved: Optional[str] = self.acronyms_mapping.get(name_upper)
        if not resolved:
            country_iso_query = self.build_query('country_iso_code', name_clean)
            countries_df = self.locations_data.query(country_iso_query)
            if not countries_df.empty:
                resolved: str = countries_df['country_name'].drop_duplicates().iloc[0]
        return resolved

    def is_country(self, name: str) -> bool:
        countries, remaining_places = self.get_countries([name], [])
        return name not in remaining_places

    def is_location(self, place: str) -> bool:
        continents, countries, regions, cities = self.find_locations([place])

        return bool(cities or regions or countries)

    def clean_sublocations(self, places):
        for place in places:
            yield self.sublocation_pattern.sub("", place)

    def extract_places(self, text=None):
        places = self.extractor.find_entities(text)
        places = list(self.clean_sublocations(places))
        return places

    def find_locations(self, places):
        continents, remaining_places = self.get_continents(places)
        countries, remaining_places = self.get_countries(places, continents)
        regions, remaining_places = self.get_regions(remaining_places, continents, countries)
        cities, remaining_places = self.get_cities(remaining_places, continents, countries, regions)

        return (
            sorted(continents),
            sorted(countries),
            sorted(regions),
            sorted(cities)
        )

    def extract_locations(self, text=None, return_strings=False):
        places = self.extract_places(text)

        continents, countries, regions, cities = self.find_locations(places)

        if return_strings:
            continents = Continent.many_to_string(continents)
            countries = Country.many_to_string(countries)
            regions = Region.many_to_string(regions)
            cities = City.many_to_string(cities)

        return continents, countries, regions, cities
