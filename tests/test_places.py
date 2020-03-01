from location_extractor.places import Extractor, Country, Region, City


def test_kenya():
    places = ['Ngong', 'Nairobi', 'Kenya']
    location_extractor = Extractor()

    expected_country = Country(name="Kenya")
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
    regions, remaining_places = location_extractor.get_regions(remaining_places, countries)
    cities, remaining_places = location_extractor.get_cities(remaining_places, countries, regions)

    expected_country = Country(name="Syria")
    expected_city = City(
        name='Aleppo',
        region=Region(name="Aleppo Governate", country=expected_country),
        country=expected_country
    )

    assert len(cities) == 1
    assert cities[-1] == expected_city
