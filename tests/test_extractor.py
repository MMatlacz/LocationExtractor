import pytest

from location_extractor.containers import City, Continent, Country, Region


def test_kenya(location_extractor):
    places = ['Ngong', 'Nairobi', 'Kenya']

    expected_continent = Continent(name='Africa')
    expected_country = Country(
        name='Kenya',
        iso_code='KE',
        continent=expected_continent,
    )
    countries, remaining_places = location_extractor.get_countries(places, [])

    assert countries == [expected_country]

    regions, remaining_places = location_extractor.get_regions(
        remaining_places,
        [],
        countries,
    )

    expected_cities = [
        City(
            name='Nairobi',
            region=Region(name='Nairobi Province', country=expected_country),
            country=expected_country,
        ),
        City(
            name='Ngong',
            region=Region(name='Kajiado District', country=expected_country),
            country=expected_country,
        ),
    ]
    cities, remaining_places = location_extractor.get_cities(
        remaining_places,
        [],
        countries,
        regions,
    )
    assert sorted(cities) == sorted(expected_cities)


def test_syria(location_extractor):
    places = ['Aleppo', 'Syria']
    countries, remaining_places = location_extractor.get_countries(places, [])
    regions, remaining_places = location_extractor.get_regions(
        remaining_places,
        [],
        countries,
    )
    cities, remaining_places = location_extractor.get_cities(
        remaining_places,
        [],
        countries,
        regions,
    )

    expected_continent = Continent(name='Asia')
    expected_country = Country(
        name='Syria',
        iso_code='SY',
        continent=expected_continent,
    )
    expected_city = City(
        name='Aleppo',
        region=Region(name='Aleppo Governorate', country=expected_country),
        country=expected_country,
    )

    assert cities == [expected_city]


@pytest.mark.parametrize(('word', 'is_location'), [
    ('warsaw', True),
    ('is', True),
    ('living', False),
    ('us', True),
    ('berlin', True),
    ('dupa', False),
])
def test_is_location(word, is_location, location_extractor):
    assert location_extractor.is_location(word) is is_location


@pytest.mark.parametrize(('word', 'is_country'), [
    ('germany', True),
    ('france', True),
    ('living', False),
    ('the us', True),
    ('berlin', False),
    ('fuzzle', False),
    ('is', True),
    ('uk', True),
    ('us', True),
])
def test_is_a_country(word, is_country, location_extractor):
    assert location_extractor.is_country(word) is is_country


@pytest.mark.parametrize(('sentence', 'expected_locations'), [
    (
        'Person living in Berlin, Germany',
        (
            [],
            ['Germany, Europe'],
            [],
            [
                'Berlin, Land Berlin, Germany, Europe',
                'Berlin, Schleswig-Holstein, Germany, Europe',
            ],
        ),
    ),
    (
        'She went to south america then moved to Hawaii and flew to Australia',
        (
            [],
            ['Australia, Oceania'],
            ['Hawaii, United States, North America'],
            [],
        ),
    ),
    (
        'Plumber in Worcester, Massachusetts',
        (
            [],
            [],
            ['Massachusetts, United States, North America'],
            ['Worcester, Massachusetts, United States, North America'],
        ),
    ),
    (
        'London, Warsaw, Czechia, Western Europe',
        (
            ['Europe'],
            ['Czechia, Europe'],
            [],
            [
                'Warsaw, Mazovia, Poland, Europe',
                'London, England, United Kingdom, Europe',
            ],
        ),
    ),
])
def tests_extract_locations_return_strings(
    sentence,
    expected_locations,
    location_extractor,
):
    locations = location_extractor.extract_locations(
        sentence,
        return_strings=True,
    )
    assert locations == expected_locations


def test_extract_location(location_extractor):
    """Ensure `Entity` subclassess are returned if ``return_string`` falsy."""
    locations = location_extractor.extract_locations(
        'Person living in Berlin, Germany',
        return_strings=False,
    )
    assert (locations[0], locations[2]) == ([], [])
    assert all(isinstance(country, Country) for country in locations[1])
    assert {country.name for country in locations[1]} == {'Germany'}
    assert all(isinstance(city, City) for city in locations[3])
    assert {city.name for city in locations[3]} == {'Berlin'}
