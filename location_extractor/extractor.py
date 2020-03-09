import os
import re
from typing import List, Set, Tuple, Optional

import pandas as pd

from location_extractor import src_dir
from location_extractor.containers import Country, Region, City, Continent
from location_extractor.helpers import capitalize_name, remove_accents
from location_extractor.named_entity_recognition.ner import NERExtractor


class Extractor:
    def __init__(self):
        self.extractor = NERExtractor()
        locations_path = os.path.join(
            src_dir, "data", "GeoLite2-City-CSV_20200303", "GeoLite2-City-Locations-en-processed.csv")
        self.locations_data = pd.read_csv(locations_path)

    def places_by_name(self, place_name, column_name) -> Optional[pd.DataFrame]:
        query = f"{column_name} = '{remove_accents(capitalize_name(place_name))}'"
        rows = self.locations_data.query(query)
        if not rows.empty:
            return rows

        return None

    def cities_for_name(self, city_name: str) -> Optional[pd.DataFrame]:
        return self.places_by_name(city_name, 'city_name')

    def regions_for_name(self, region_name: str) -> Optional[pd.DataFrame]:
        return self.places_by_name(region_name, 'subdivision_name')

    def get_continents(self, places) -> Tuple[List[Continent], Set[str]]:
        continents = set()
        remaining_places = set()
        for place in places:
            name_clean = remove_accents(capitalize_name(place))
            continent_query = f"continent_name == '{name_clean}'"
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
            resolved = self.find_acronym(place)
            if resolved:
                name_clean = remove_accents(capitalize_name(resolved))
            else:
                name_clean = remove_accents(capitalize_name(place))

            query = f"country_name == '{name_clean}'"
            countries_df = self.locations_data.query(query)

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
            name_clean = remove_accents(capitalize_name(place))
            query = f"subdivision_name == '{name_clean}'"
            regions_df = self.locations_data.query(query)

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
            query = f'city_name == "{capitalize_name(remove_accents(place))}"'
            cities_df = self.locations_data.query(query)

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

    def find_acronym(self, name):
        name_clean = remove_accents(name).upper()
        name_clean = re.sub(r"(^|\s)(the)(\s|$)", "", name_clean, flags=re.IGNORECASE)
        if name_clean == "UK":
            name_clean = "GB"
        elif name_clean == "USA":
            name_clean = "US"
        query = f"country_iso_code == '{name_clean}'"
        countries_df = self.locations_data.query(query)
        if not countries_df.empty:
            return countries_df['country_name'].drop_duplicates().iloc[0]

    def is_a_country(self, name: str) -> bool:
        countries, remaining_places = self.get_countries([name], [])
        return name not in remaining_places

    def is_location(self, place: str) -> bool:
        continents, countries, regions, cities = self.find_locations([place])

        if cities or regions or countries:
            return True
        else:
            return False

    def clean_sublocations(self, places):
        pattern = re.compile(r"(west|south|north|east)(ern)?", re.IGNORECASE)
        for place in places:
            yield pattern.sub("", place)

    def extract_places(self, text=None):
        places = self.extractor.find_entities(text)
        places = list(self.clean_sublocations(places))
        return places

    def find_locations(self, places):
        continents, remaining_places = self.get_continents(places)
        countries, remaining_places = self.get_countries(places, continents)
        regions, remaining_places = self.get_regions(remaining_places, continents, countries)
        cities, remaining_places = self.get_cities(remaining_places, continents, countries, regions)

        continents = sorted(continents)
        countries = sorted(countries)
        regions = sorted(regions)
        cities = sorted(cities)

        return continents, countries, regions, cities

    def extract_locations(self, text=None, return_strings=False):
        places = self.extract_places(text)

        continents, countries, regions, cities = self.find_locations(places)

        if return_strings:
            continents = Continent.many_to_string(continents)
            countries = Country.many_to_string(countries)
            regions = Region.many_to_string(regions)
            cities = City.many_to_string(cities)

        return continents, countries, regions, cities
