from dataclasses import dataclass
from typing import List, Optional
import abc


class Entity:
    @abc.abstractmethod
    def to_string(self) -> str:
        pass

    @classmethod
    def many_to_string(cls, entities):
        return [entity.to_string() for entity in entities]

    @classmethod
    def from_dict(cls, **kwargs):
        pass

    @classmethod
    def from_dicts(cls, dictionaries=List[dict]):
        return [cls.from_dict(**dictionary) for dictionary in dictionaries]


@dataclass(frozen=True, eq=True)
class Continent(Entity):
    name: str

    def __lt__(self, other):
        return self.name < other.name

    @classmethod
    def many_to_list(cls, continents: List):
        return [continent.name for continent in continents]

    def to_string(self) -> str:
        return f'{self.name}'

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(name=kwargs.get("continent_name"))


@dataclass(frozen=True, eq=True)
class Country(Entity):
    name: str
    iso_code: str
    continent: Continent

    def __lt__(self, other):
        return (self.continent, self.name) < (other.continent, other.name)

    @classmethod
    def many_to_list(cls, countries: List):
        return [country.name for country in countries]

    def to_string(self) -> str:
        return f'{self.name}'

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(name=kwargs.get("country_name"), iso_code=kwargs.get("country_iso_code"),
                   continent=Continent.from_dict(**kwargs))


@dataclass(frozen=True, eq=True)
class Region(Entity):
    name: str
    country: Country

    def __lt__(self, other):
        return (self.country, self.name) < (other.country, other.name)

    @classmethod
    def many_to_list(cls, regions: List):
        return [region.name for region in regions]

    def to_string(self) -> str:
        return f'{self.name}, {self.country.name}'

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(name=kwargs.get("subdivision_name"), country=Country.from_dict(**kwargs))


@dataclass(frozen=True, eq=True)
class City(Entity):
    name: str
    region: Optional[Region]
    country: Country

    def __lt__(self, other):
        return (self.country, self.region, self.name) < (other.country, other.region, other.name)

    @classmethod
    def many_to_list(cls, cities: List):
        return [(city.name, city.region.name, city.country.name) for city in cities]

    def to_string(self):
        return f'{self.name}, {self.region.to_string()}'

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(name=kwargs.get("city_name"), region=Region.from_dict(**kwargs), country=Country.from_dict(**kwargs))
