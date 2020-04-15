import abc
from dataclasses import dataclass
from typing import List, Optional

from location_extractor.clients import LocationDTO


class Entity(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_dto(cls, dto: LocationDTO) -> 'Entity':
        """
        Create ``Entity`` instance from ``LocationDTO``.
        :param dto: LocationDTO
        :return: Entity
        """

    @classmethod
    @abc.abstractmethod
    def from_dtos(cls, dtos: List[LocationDTO]) -> List['Entity']:
        """
        Convert list of dictionaries to a list of entities
        """

    @classmethod
    def many_to_string(cls, entities: List['Entity']) -> List[str]:
        return [str(entity) for entity in entities]


@dataclass(frozen=True, eq=True)
class Continent(Entity):
    name: str

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_dto(cls, dto: LocationDTO) -> 'Continent':
        return cls(
            name=dto.continent_name
        )

    @classmethod
    def from_dtos(cls, dtos: List[LocationDTO]) -> List['Continent']:
        return [cls.from_dto(dto) for dto in dtos]


@dataclass(frozen=True, eq=True)
class Country(Entity):
    name: str
    iso_code: str
    continent: Continent

    def __lt__(self, other):
        return (self.continent, self.name) < (other.continent, other.name)

    def __str__(self) -> str:
        return f'{self.name}, {self.continent}'

    @classmethod
    def from_dto(cls, dto: LocationDTO) -> 'Country':
        return cls(
            name=dto.country_name,
            iso_code=dto.country_iso_code,
            continent=Continent.from_dto(dto)
        )

    @classmethod
    def from_dtos(cls, dtos: List[LocationDTO]) -> List['Country']:
        return [cls.from_dto(dto) for dto in dtos]


@dataclass(frozen=True, eq=True)
class Region(Entity):
    name: str
    country: Country

    def __lt__(self, other):
        return (self.country, self.name) < (other.country, other.name)

    def __str__(self) -> str:
        return f'{self.name}, {self.country}'

    @classmethod
    def from_dto(cls, dto: LocationDTO) -> 'Region':
        return cls(
            name=dto.subdivision_name,
            country=Country.from_dto(dto)
        )

    @classmethod
    def from_dtos(cls, dtos: List[LocationDTO]) -> List['Region']:
        return [cls.from_dto(dto) for dto in dtos]


@dataclass(frozen=True, eq=True)
class City(Entity):
    name: str
    region: Optional[Region]
    country: Country

    def __lt__(self, other):
        return (self.country, self.region, self.name) < (other.country, other.region, other.name)

    def __str__(self) -> str:
        return f'{self.name}, {self.region}'

    @classmethod
    def from_dto(cls, dto: LocationDTO) -> 'City':
        return cls(
            name=dto.city_name,
            region=Region.from_dto(dto),
            country=Country.from_dto(dto)
        )

    @classmethod
    def from_dtos(cls, dtos: List[LocationDTO]) -> List['City']:
        return [cls.from_dto(dto) for dto in dtos]
