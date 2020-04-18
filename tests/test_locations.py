import pytest


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
    assert location_extractor.places_by_name(name, column_name)
