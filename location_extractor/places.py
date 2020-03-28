import csv
import os
import re
import sqlite3

from typing import List, Set, Tuple

import pandas as pd

from location_extractor import src_dir
from location_extractor.containers import City, Country, Region
from location_extractor.extraction import NERExtractor
from location_extractor.helpers import capitalize_name
from location_extractor.pycountry_helper import PycountryHelper
from location_extractor.utils import fuzzy_match


class Extractor:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(src_dir, "data", "locs.db"))
        if not self.db_has_data():
            self.populate_db()

        self.extractor = NERExtractor()

        self.pycountry_helper = PycountryHelper()

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

    def is_a_country(self, country_name: str):
        clean_country_name, _ = self.pycountry_helper.get_country_name_and_iso_code(country_name)

        if clean_country_name:
            return True
        else:
            query = f"SELECT * FROM cities WHERE country_name = '{capitalize_name(country_name)}'"
            countries_df = pd.read_sql(query, self.conn)
            return countries_df.shape[0] > 0

    def places_by_name(self, place_name, column_name):
        cur = self.conn.cursor()
        # TODO: properly escape `column_name`
        cur.execute(
            f'SELECT * FROM cities WHERE {column_name} = ?',
            (place_name,),
        )
        rows = list(cur.fetchall())
        return rows or None

    def cities_for_name(self, city_name):
        return self.places_by_name(city_name, 'city_name')

    def regions_for_name(self, region_name):
        return self.places_by_name(region_name, 'subdivision_name')

    def resolve_acronyms(self, place: str):
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
            clean_country = self.pycountry_helper.get_country_name_and_iso_code(resolved)
            if clean_country:
                country = clean_country

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
                regions = self.pycountry_helper.get_region_names(country)
                for region in regions:
                    if fuzzy_match(place, region.name):
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
            capitalised_place = f'"{capitalize_name(place)}"'
            iso_codes = [country.iso_code for country in countries]
            query = f'''
                SELECT * FROM cities 
                WHERE 
                    city_name = {capitalised_place} 
            '''
            cities_df = pd.read_sql(query, self.conn)

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

    def is_location(self, place: str):
        countries, remaining_places = self.get_countries([place])
        regions, remaining_places = self.get_regions(remaining_places, countries)
        cities, remaining_places = self.get_cities(remaining_places, countries, regions)

        if cities or regions or countries:
            return True
        else:
            return False
