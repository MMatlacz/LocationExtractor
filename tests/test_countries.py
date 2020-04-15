import pytest

from location_extractor.containers import Country, Location


@pytest.mark.parametrize(
    ["places", "expected_countries"],
    [
        (['Ngong', 'Nairobi', 'Kenya'], ['Kenya, Africa']),
        (['Aleppo', 'Syria'], ['Syria, Asia']),
        (['Warsaw', 'Poland'], ['Poland, Europe']),
        (['Germany', 'Poland'], ['Germany, Europe', 'Poland, Europe']),
        (['USA', 'UK'], ['United Kingdom, Europe', 'United States, North America']),
        (['The USA', 'The UK'], ['United Kingdom, Europe', 'United States, North America']),
        (['Ukraine'], ['Ukraine, Europe']),
    ]
)
def test_get_countries(places, expected_countries, location_extractor):
    places = [Location(name=place) for place in places]
    countries, _ = location_extractor.get_countries(places, [])
    assert sorted(Country.many_to_string(countries)) == expected_countries
