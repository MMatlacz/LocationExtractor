import pytest

from location_extractor.containers import City
from location_extractor.places import Extractor


@pytest.fixture()
def location_extractor():
    return Extractor()


@pytest.mark.parametrize(
    ["places", "expected_city"],
    [
        (['Poland', 'Warsaw'], [('Warsaw', 'Mazovia', 'Poland')]),
        (['Warsaw', 'Poland'], [('Warsaw', 'Mazovia', 'Poland')]),
        (['Berlin', 'Poland'], [('Berlin', 'Land Berlin', 'Germany'),
                                ('Berlin', 'Schleswig-Holstein', 'Germany'),
                                ('Berlin', 'Connecticut', 'United States'),
                                ('Berlin', 'Georgia', 'United States'),
                                ('Berlin', 'Maryland', 'United States'),
                                ('Berlin', 'Massachusetts', 'United States'),
                                ('Berlin', 'New Hampshire', 'United States'),
                                ('Berlin', 'New Jersey', 'United States'),
                                ('Berlin', 'New York', 'United States'),
                                ('Berlin', 'Pennsylvania', 'United States'),
                                ('Berlin', 'Wisconsin', 'United States')]),
        (['Berlin', 'United States'], [('Berlin', 'Connecticut', 'United States'),
                                       ('Berlin', 'Georgia', 'United States'),
                                       ('Berlin', 'Maryland', 'United States'),
                                       ('Berlin', 'Massachusetts', 'United States'),
                                       ('Berlin', 'New Hampshire', 'United States'),
                                       ('Berlin', 'New Jersey', 'United States'),
                                       ('Berlin', 'New York', 'United States'),
                                       ('Berlin', 'Pennsylvania', 'United States'),
                                       ('Berlin', 'Wisconsin', 'United States')]),
        (['Berlin', 'Germany'], [('Berlin', 'Land Berlin', 'Germany'),
                                 ('Berlin', 'Schleswig-Holstein', 'Germany')]),
    ]
)
def test_get_cities(places, expected_city, location_extractor):
    countries, rest = location_extractor.get_countries(places)
    regions, rest = location_extractor.get_regions(rest, countries)
    cities, _ = location_extractor.get_cities(rest, countries, regions)

    assert sorted(City.many_to_list(cities), key=lambda x: (x[2], x[1])) == expected_city


@pytest.mark.parametrize(
    ["places", "expected_city"],
    [
        (["Gdańsk"], [('Gdansk', 'Pomerania', 'Poland')]),
        (["Gdansk"], [('Gdansk', 'Pomerania', 'Poland')]),
        (["Kraków"], [('Krakow', 'Lesser Poland', 'Poland'), ('Krakow', 'Wisconsin', 'United States')]),
        (["Krakow"], [('Krakow', 'Lesser Poland', 'Poland'), ('Krakow', 'Wisconsin', 'United States')]),
    ]
)
def test_extract_cities(places, expected_city, location_extractor):
    cities, _ = location_extractor.get_cities(places, [], [])

    assert City.many_to_list(cities) == expected_city
