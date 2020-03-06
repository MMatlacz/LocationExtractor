import pandas as pd
import pytest

from location_extractor.places import (
    City,
    Country,
    Region,
)


def test_kenya(location_extractor):
    places = ['Ngong', 'Nairobi', 'Kenya']

    expected_country = Country(name="Kenya", iso_code='KE')
    countries, remaining_places = location_extractor.get_countries(places)

    assert countries == [expected_country]

    regions, remaining_places = location_extractor.get_regions(remaining_places, countries)

    expected_cities = [
        City(
            name="Nairobi",
            region=Region(name='Nairobi Province', country=expected_country),
            country=expected_country
        ),
        City(
            name="Ngong",
            region=Region(name='Kajiado District', country=expected_country),
            country=expected_country
        )
    ]
    cities, remaining_places = location_extractor.get_cities(remaining_places, countries, regions)
    sorted_cities = sorted(cities, key=lambda x: (x.country.name, x.region.name, x.name))
    sorted_expected = sorted(expected_cities, key=lambda x: (x.country.name, x.region.name, x.name))
    assert sorted_cities == sorted_expected


def test_syria(location_extractor):
    places = ['Aleppo', 'Syria']
    countries, remaining_places = location_extractor.get_countries(places)
    regions, remaining_places = location_extractor.get_regions(remaining_places, countries)
    cities, remaining_places = location_extractor.get_cities(remaining_places, countries, regions)

    expected_country = Country(name="Syria", iso_code='SY')
    expected_city = City(
        name='Aleppo',
        region=Region(name="Aleppo Governorate", country=expected_country),
        country=expected_country
    )

    assert cities == [expected_city]


@pytest.mark.parametrize(
    ["word", "is_location"],
    [
        ('warsaw', True),
        ('is', False),
        ('living', False),
        ('us', True),
        ('berlin', True),
        ('dupa', False),
    ]
)
def test_is_location(word, is_location, location_extractor):
    assert location_extractor.is_location(word) is is_location


@pytest.mark.parametrize(
    ["word", "is_location"],
    [
        ('germany', True),
        ('france', True),
        ('living', False),
        ('us', False),
        ('berlin', False),
        ('dupa', False),
    ]
)
def test_is_location(word, is_location, location_extractor):
    assert location_extractor.is_a_country(word) is is_location


@pytest.mark.parametrize(('name', 'column_name'), [
    ("Campbell's Bay", 'city_name'),
    ("Côtes-d'Armor", 'subdivision_name'),
    ("Ta' Xbiex", 'subdivision_name'),
    ("Departement de l'Ouest", 'subdivision_name'),
])
def test_issue8_single_quote_in_place_name(
        location_extractor,
        name,
        column_name,
):
    assert isinstance(location_extractor.places_by_name(name, column_name), pd.DataFrame)
