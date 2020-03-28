import pytest

from location_extractor.containers import Country


@pytest.mark.parametrize(
    ["places", "expected_countries"],
    [
        (['Ngong', 'Nairobi', 'Kenya'], ['Kenya']),
        (['Aleppo', 'Syria'], ['Syria']),
        (['Warsaw', 'Poland'], ['Poland']),
        (['Germany', 'Poland'], ['Germany', 'Poland']),
        (['USA', 'UK'], ['United Kingdom', 'United States']),
        (['The USA', 'The UK'], ['United Kingdom', 'United States']),
        (['Ukraine'], ['Ukraine']),
    ]
)
def test_get_countries(places, expected_countries, location_extractor):
    countries, _ = location_extractor.get_countries(places, [])
    assert sorted(Country.many_to_list(countries)) == expected_countries
