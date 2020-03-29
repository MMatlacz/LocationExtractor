import pytest

from location_extractor.containers import City


@pytest.mark.parametrize(('places', 'expected_cities'), [
    (
        ['Poland', 'Warsaw'],
        [('Warsaw', 'Mazovia', 'Poland', 'Europe')],
    ),
    (
        ['Warsaw', 'Poland'],
        [('Warsaw', 'Mazovia', 'Poland', 'Europe')],
    ),
    (
        ['Berlin', 'Poland'],
        [
            ('Berlin', 'Land Berlin', 'Germany', 'Europe'),
            ('Berlin', 'Schleswig-Holstein', 'Germany', 'Europe'),
            ('Berlin', 'Connecticut', 'United States', 'North America'),
            ('Berlin', 'Georgia', 'United States', 'North America'),
            ('Berlin', 'Maryland', 'United States', 'North America'),
            ('Berlin', 'Massachusetts', 'United States', 'North America'),
            ('Berlin', 'New Hampshire', 'United States', 'North America'),
            ('Berlin', 'New Jersey', 'United States', 'North America'),
            ('Berlin', 'New York', 'United States', 'North America'),
            ('Berlin', 'Pennsylvania', 'United States', 'North America'),
            ('Berlin', 'Wisconsin', 'United States', 'North America'),
        ],
    ),
    (
        ['Berlin', 'United States'],
        [
            ('Berlin', 'Connecticut', 'United States', 'North America'),
            ('Berlin', 'Georgia', 'United States', 'North America'),
            ('Berlin', 'Maryland', 'United States', 'North America'),
            ('Berlin', 'Massachusetts', 'United States', 'North America'),
            ('Berlin', 'New Hampshire', 'United States', 'North America'),
            ('Berlin', 'New Jersey', 'United States', 'North America'),
            ('Berlin', 'New York', 'United States', 'North America'),
            ('Berlin', 'Pennsylvania', 'United States', 'North America'),
            ('Berlin', 'Wisconsin', 'United States', 'North America'),
        ],
    ),
    (
        ['Berlin', 'Germany'],
        [
            ('Berlin', 'Land Berlin', 'Germany', 'Europe'),
            ('Berlin', 'Schleswig-Holstein', 'Germany', 'Europe'),
        ],
    ),
])
def test_get_cities(places, expected_cities, location_extractor):
    expected_cities = list(map(', '.join, expected_cities))

    countries, rest = location_extractor.get_countries(places, continents=[])
    regions, rest = location_extractor.get_regions(
        rest,
        continents=[],
        countries=countries,
    )
    cities, _ = location_extractor.get_cities(
        rest,
        continents=[],
        countries=countries,
        regions=regions,
    )
    assert sorted(City.many_to_string(cities)) == sorted(expected_cities)


@pytest.mark.parametrize(('places', 'expected_cities'), [
    (['Gdańsk'], [('Gdansk', 'Pomerania', 'Poland', 'Europe')]),
    (['Gdansk'], [('Gdansk', 'Pomerania', 'Poland', 'Europe')]),
    (
        ['Kraków'],
        [
            ('Krakow', 'Lesser Poland', 'Poland', 'Europe'),
            ('Krakow', 'Wisconsin', 'United States', 'North America'),
        ],
    ),
    (
        ['Krakow'],
        [
            ('Krakow', 'Lesser Poland', 'Poland', 'Europe'),
            ('Krakow', 'Wisconsin', 'United States', 'North America'),
        ],
    ),
])
def test_extract_cities(places, expected_cities, location_extractor):
    expected_cities = list(map(', '.join, expected_cities))

    cities, _ = location_extractor.get_cities(places, [], [], [])

    assert sorted(City.many_to_string(cities)) == sorted(expected_cities)
