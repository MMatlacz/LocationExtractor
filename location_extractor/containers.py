from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Country:
    name: str
    iso_code: str

    @classmethod
    def many_to_list(cls, countries: List):
        return [country.name for country in countries]


@dataclass
class Region:
    name: str
    country: Country


@dataclass
class City:
    name: str
    region: Optional[Region]
    country: Country

    @classmethod
    def many_to_list(cls, cities: List):
        return [(city.name, city.region.name, city.country.name) for city in cities]
