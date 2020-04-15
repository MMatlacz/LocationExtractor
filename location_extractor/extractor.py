import re
from typing import List, Set, Tuple, Optional

from location_extractor.clients import DBClient, LocationDTO
from location_extractor.containers import Country, Region, City, Continent, Location
from location_extractor.helpers import remove_accents
from location_extractor.named_entity_recognition.ner import NERExtractor


class Extractor:
    clean_acronym_pattern = re.compile(
        r"(^|\s)(the)(\s|$)", flags=re.IGNORECASE
    )

    def __init__(self) -> None:
        self.extractor = NERExtractor()

        self.dbclient = DBClient()

        self.acronyms_mapping = {
            "UK": "United Kingdom",
            "USA": "United States",
        }

    def places_by_name(self, place_name, column_name) -> List[LocationDTO]:
        rows = self.dbclient.fetch_all(column_name, place_name)
        return rows

    def cities_for_name(self, city_name: str) -> List[LocationDTO]:
        return self.places_by_name(city_name, 'city_name')

    def regions_for_name(self, region_name: str) -> List[LocationDTO]:
        return self.places_by_name(region_name, 'subdivision_name')

    def get_continents(self, places: List[Location]) -> Tuple[List[Continent], Set[Location]]:
        pattern = re.compile(
            r"(?P<sublocation>.*\s+)?(?P<continent>Europe|Asia|South America|North America|Oceania|Africa)", flags=re.I)
        continents = set()
        remaining_places = set()
        for place in places:
            if place.type == "CONTINENT":
                match = pattern.match(place.name).groupdict(default="")
                continents.add(Continent(
                    name=match.get("continent").strip(),
                    sublocation=match.get("sublocation").strip()
                ))
            else:
                remaining_places.add(place)

        return list(continents), remaining_places

    def get_countries(self, places: List[Location], continents: List[Continent]) -> Tuple[List[Country], Set[Location]]:
        countries = set()
        remaining_places = set()
        for place in places:
            resolved = self.resolve_acronym(place.name)
            countries_dto = self.dbclient.fetch_all('country_name', resolved or place.name)

            potential_countries = Country.from_dtos(countries_dto)

            countries_on_continents = [country for country in potential_countries if country.continent in continents]

            if countries_on_continents:
                countries = countries.union(countries_on_continents)
            elif potential_countries:
                countries = countries.union(potential_countries)
            else:
                remaining_places.add(place)

        return list(countries), remaining_places

    def get_regions(self, places: Set[Location], continents: List[Continent],
                    countries: List[Country]) -> Tuple[List[Region], Set[Location]]:
        regions = set()
        remaining_places = set()

        for place in places:
            regions_dto = self.dbclient.fetch_all('subdivision_name', place.name)

            potential_regions = Region.from_dtos(regions_dto)

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

    def get_cities(self, places: Set[Location], continents: List[Continent], countries: List[Country],
                   regions: List[Region]) -> Tuple[List[City], Set[Location]]:
        remaining_places = set()
        cities = set()
        for place in places:
            cities_dto = self.dbclient.fetch_all('city_name', place.name)
            potential_cities = City.from_dtos(cities_dto)

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
            countries_dto = self.dbclient.fetch_one_raw('country_iso_code', name_clean, columns='country_name')
            if countries_dto:
                resolved = countries_dto[0]
        return resolved

    def is_country(self, name: Location) -> bool:
        countries, remaining_places = self.get_countries([name], [])
        return name not in remaining_places

    def is_location(self, place: Location) -> bool:
        continents, countries, regions, cities = self.find_locations([place])

        return bool(cities or regions or countries)

    def extract_places(self, text=None):
        places = self.extractor.find_entities(text)
        return places

    def find_locations(self, places: List[Location]):
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
