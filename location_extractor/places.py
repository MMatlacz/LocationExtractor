import csv
import os
import sqlite3
from dataclasses import dataclass
from pprint import pprint
from typing import List, Set, Tuple, Optional

import pandas as pd
import pycountry

from location_extractor import src_dir
from location_extractor.extraction import NERExtractor
from location_extractor.utils import fuzzy_match


@dataclass
class Country:
    name: str


@dataclass
class Region:
    name: str
    country: Country


@dataclass
class City:
    name: str
    region: Optional[Region]
    country: Country


class Extractor:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(src_dir, "data", "locs.db"))
        if not self.db_has_data():
            self.populate_db()

        dictionary_path = os.path.join(src_dir, "data", "ISO3166ErrorDictionary.csv")
        self.dictionary = pd.read_csv(dictionary_path)

        self.extractor = NERExtractor()

    def populate_db(self):
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS cities")

        cur.execute(
            """CREATE TABLE cities(
                    geoname_id INTEGER, 
                    continent_code TEXT, 
                    continent_name TEXT, 
                    country_iso_code TEXT, 
                    country_name TEXT, 
                    subdivision_iso_code TEXT, 
                    subdivision_name TEXT, 
                    city_name TEXT, 
                    metro_code TEXT, 
                    time_zone TEXT
                )
            """)
        with open(src_dir + "/data/GeoLite2-City-Locations.csv", "r") as info:
            reader = csv.reader(info)
            for row in reader:
                cur.execute("INSERT INTO cities VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", row)

            self.conn.commit()

    def db_has_data(self):
        cur = self.conn.cursor()

        cur.execute("SELECT Count(*) FROM sqlite_master WHERE name='cities';")
        data = cur.fetchone()[0]

        if data > 0:
            cur.execute("SELECT Count(*) FROM cities")
            data = cur.fetchone()[0]
            return data > 0

        return False

    def capitalize_region_name(self, place):
        splitted = place.split(' ')
        capitalized = ' '.join([subword.capitalize() for subword in splitted])
        splitted = capitalized.split('-')
        capitalized = ' '.join([subword.capitalize() for subword in splitted])
        return capitalized

    def correct_misspelling(self, place_name: str):
        result = self.dictionary[self.dictionary["data.un.org entry"] == place_name]["ISO3166 name or code"]
        if result.shape[0] > 0:
            return result.iloc[0]
        else:
            return place_name

    def is_a_country(self, country):
        try:
            found_index = pycountry.countries.get(name=country)
            if not found_index:
                return False
            else:
                return True
        except KeyError:
            return False

    def places_by_name(self, place_name, column_name):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM cities WHERE {column_name} = '{place_name}'")
        rows = cur.fetchall()

        if len(rows) > 0:
            return rows

        return None

    def cities_for_name(self, city_name):
        return self.places_by_name(city_name, 'city_name')

    def regions_for_name(self, region_name):
        return self.places_by_name(region_name, 'subdivision_name')

    def get_region_names(self, country: Country):
        try:
            obj = pycountry.countries.get(name=country.name)
            regions = pycountry.subdivisions.get(country_code=obj.alpha_2)
        except KeyError:
            return []

        return [Region(name=region.name, country=country) for region in regions]

    def is_unused(self, place_name, countries, cities, regions):
        places = [*countries, *cities, *regions]
        without_misspelling = self.correct_misspelling(place_name)
        return without_misspelling not in places

    def region_match(self, place_name, region_name):
        return fuzzy_match(place_name, region_name)

    def get_countries(self, places) -> Tuple[List[Country], Set[str]]:
        places_without_misspellings = map(self.correct_misspelling, places)
        countries = []
        remaining_places = set()
        cleaned_and_original = [*places_without_misspellings, *places]
        for i, cleaned in enumerate(cleaned_and_original):
            original = places[i % len(places)]
            if self.is_a_country(cleaned):
                country = Country(cleaned)

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
                regions = self.get_region_names(country)
                for region in regions:
                    if self.region_match(place, region.name):
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
            capitalised_place = f'"{self.capitalize_region_name(place)}"'
            query = f'SELECT * FROM cities WHERE city_name = {capitalised_place}'
            cities_df = pd.read_sql(query, self.conn)

            found_cities = []
            for i, row in cities_df.iterrows():
                city_name = row.city_name
                region_name = row.subdivision_name

                country = Country(name=row.country_name)
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

    def get_other(self, places, countries, regions, cities):
        other = []
        for place in places:
            if self.is_unused(place, countries=countries, regions=regions, cities=cities):
                other.append(place)
        return other

    def extract_locations(self, text=None):
        places = self.extractor.find_entities(text)

        place_context = Extractor()
        countries, remaining_places = place_context.get_countries(places)
        regions, remaining_places = place_context.get_regions(remaining_places, countries)
        cities, remaining_places = place_context.get_cities(remaining_places, countries, regions)
        # place_context.set_other()

        return countries, regions, cities, remaining_places

    def is_location(self, place: str):
        place_context = Extractor()
        countries, remaining_places = place_context.get_countries([place])
        regions, remaining_places = place_context.get_regions(remaining_places, countries)
        cities, remaining_places = place_context.get_cities(remaining_places, countries, regions)

        if cities or regions or countries:
            return True
        else:
            return False


if __name__ == "__main__":
    locations_extractor = Extractor()
    countries, regions, cities, remaining_places = locations_extractor.extract_locations(
        "living in")

    pprint(countries)
    pprint(regions)
    pprint(cities)
    pprint(remaining_places)

    pprint(locations_extractor.is_location("berlin"))
