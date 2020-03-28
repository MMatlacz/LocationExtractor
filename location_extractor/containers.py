from dataclasses import dataclass
from typing import List, Optional
import abc

from location_extractor.clients import LocationDTO


class Entity(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_dto(cls, dto: LocationDTO):
        """
        Convert dictionary to Entity
        :param dto: LocationDTO
        :return: Entity
        """

    @classmethod
    def from_dtos(cls, dtos: List[LocationDTO]):
        """
        Convert list of dictionaries to a list of entities
        :param dtos: List[LocationDTO]
        :return: List[Entity]
        """
        return [cls.from_dto(dto) for dto in dtos]

    @classmethod
    def many_to_string(cls, entities: List):
        return [str(entity) for entity in entities]


@dataclass(frozen=True, eq=True)
class Continent(Entity):
    name: str

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def many_to_list(cls, continents: List):
        return [continent.name for continent in continents]

    @classmethod
    def from_dto(cls, dto: LocationDTO):
        return cls(
            name=dto.continent_name
        )


@dataclass(frozen=True, eq=True)
class Country(Entity):
    name: str
    iso_code: str
    continent: Continent

    def __lt__(self, other):
        return (self.continent, self.name) < (other.continent, other.name)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def many_to_list(cls, countries: List):
        return [country.name for country in countries]

    @classmethod
    def from_dto(cls, dto: LocationDTO):
        return cls(
            name=dto.country_name,
            iso_code=dto.country_iso_code,
            continent=Continent.from_dto(dto)
        )


@dataclass(frozen=True, eq=True)
class Region(Entity):
    name: str
    country: Country

    def __lt__(self, other):
        return (self.country, self.name) < (other.country, other.name)

    def __str__(self) -> str:
        return f'{self.name}, {self.country.name}'

    @classmethod
    def many_to_list(cls, regions: List):
        return [region.name for region in regions]

    @classmethod
    def from_dto(cls, dto: LocationDTO):
        return cls(
            name=dto.subdivision_name,
            country=Country.from_dto(dto)
        )


@dataclass(frozen=True, eq=True)
class City(Entity):
    name: str
    region: Optional[Region]
    country: Country

    def __lt__(self, other):
        return (self.country, self.region, self.name) < (other.country, other.region, other.name)

    def __str__(self):
        return f'{self.name}, {self.region}'

    @classmethod
    def many_to_list(cls, cities: List):
        return [(city.name, city.region.name, city.country.name) for city in cities]

    @classmethod
    def from_dto(cls, dto: LocationDTO):
        return cls(
            name=dto.city_name,
            region=Region.from_dto(dto),
            country=Country.from_dto(dto)
        )
