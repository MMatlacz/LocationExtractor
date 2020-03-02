import pytest

from location_extractor.places import Extractor, Country, Region, City


def test_kenya():
    places = ['Ngong', 'Nairobi', 'Kenya']
    location_extractor = Extractor()

    expected_country = Country(name="Kenya", iso_code='KE')
    countries, remaining_places = location_extractor.get_countries(places)

    assert len(countries) == 1
    assert countries[-1] == expected_country

    regions, remaining_places = location_extractor.get_regions(remaining_places, countries)
    assert len(regions) == 0

    expected_city = City(
        name="Nairobi",
        region=Region(name='Nairobi Province', country=expected_country),
        country=expected_country
    )
    cities, remaining_places = location_extractor.get_cities(remaining_places, countries, regions)

    assert len(cities) == 1
    assert cities[-1] == expected_city


def test_syria():
    places = ['Aleppo', 'Syria']
    location_extractor = Extractor()
    countries, remaining_places = location_extractor.get_countries(places)
    print(countries)
    regions, remaining_places = location_extractor.get_regions(remaining_places, countries)
    cities, remaining_places = location_extractor.get_cities(remaining_places, countries, regions)

    expected_country = Country(name="Syria", iso_code='SY')
    expected_city = City(
        name='Aleppo',
        region=Region(name="Aleppo Governate", country=expected_country),
        country=expected_country
    )

    assert len(cities) == 1
    assert cities[-1] == expected_city


@pytest.fixture()
def location_extractor():
    return Extractor()


@pytest.mark.parametrize(
    ["places", "expected_countries"],
    [
        (['Ngong', 'Nairobi', 'Kenya'], ['Kenya']),
        (['Aleppo', 'Syria'], ['Syrian Arab Republic']),
        (['Warsaw', 'Poland'], ['Poland']),
        (['Germany', 'Poland'], ['Germany', 'Poland']),
        (['USA', 'UK'], ['United States', 'United Kingdom']),
        (['The USA', 'The UK'], ['United States', 'United Kingdom']),
        (['US'], ['United States']),
        (['Ukraine'], ['Ukraine']),
    ]
)
def test_get_countries(location_extractor, places, expected_countries):
    countries, _ = location_extractor.get_countries(places)
    assert Country.many_to_list(countries) == expected_countries


@pytest.mark.parametrize(
    ["places", "expected_city"],
    [
        (['Poland', 'Warsaw'], [('Warsaw', 'Masovian Voivodeship', 'Poland')]),
        (['Warsaw', 'Poland'], [('Warsaw', 'Masovian Voivodeship', 'Poland')]),
        (['Berlin', 'Poland'], [('Berlin', 'Land Berlin', 'Germany'),
                                ('Berlin', 'Maryland', 'United States'),
                                ('Berlin', 'Connecticut', 'United States'),
                                ('Berlin', 'Ohio', 'United States'),
                                ('Berlin', 'New Hampshire', 'United States'),
                                ('Berlin', 'Massachusetts', 'United States'),
                                ('Berlin', 'Pennsylvania', 'United States'),
                                ('Berlin', 'New Jersey', 'United States'),
                                ('Berlin', 'Wisconsin', 'United States'),
                                ('Berlin', 'Georgia', 'United States'),
                                ('Berlin', 'Schleswig-Holstein', 'Germany')]),
        (['Berlin', 'United States'], [('Berlin', 'Maryland', 'United States'),
                                       ('Berlin', 'Connecticut', 'United States'),
                                       ('Berlin', 'Ohio', 'United States'),
                                       ('Berlin', 'New Hampshire', 'United States'),
                                       ('Berlin', 'Massachusetts', 'United States'),
                                       ('Berlin', 'Pennsylvania', 'United States'),
                                       ('Berlin', 'New Jersey', 'United States'),
                                       ('Berlin', 'Wisconsin', 'United States'),
                                       ('Berlin', 'Georgia', 'United States')]),
        (['Berlin', 'Germany'], [('Berlin', 'Land Berlin', 'Germany'),
                                 ('Berlin', 'Schleswig-Holstein', 'Germany')]),
    ]
)
def test_get_cities(location_extractor, places, expected_city):
    countries, rest = location_extractor.get_countries(places)
    regions, rest = location_extractor.get_regions(rest, countries)
    cities, _ = location_extractor.get_cities(rest, countries, regions)

    assert City.many_to_list(cities) == expected_city
