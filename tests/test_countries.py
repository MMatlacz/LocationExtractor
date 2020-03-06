import pytest

from location_extractor.containers import Country
from location_extractor.places import Extractor


@pytest.fixture()
def location_extractor():
    return Extractor()


@pytest.mark.parametrize(
    ["places", "expected_countries"],
    [
        (['Ngong', 'Nairobi', 'Kenya'], ['Kenya']),
        (['Aleppo', 'Syria'], ['Syria']),
        (['Warsaw', 'Poland'], ['Poland']),
        (['Germany', 'Poland'], ['Germany', 'Poland']),
        (['USA', 'UK'], ['United States', 'United Kingdom']),
        (['The USA', 'The UK'], ['United States', 'United Kingdom']),
        (['Ukraine'], ['Ukraine']),
    ]
)
def test_get_countries(places, expected_countries, location_extractor):
    countries, _ = location_extractor.get_countries(places)
    assert Country.many_to_list(countries) == expected_countries
