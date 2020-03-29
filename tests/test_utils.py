import pytest

from location_extractor.utils import fuzzy_match


@pytest.mark.parametrize(('name', 'option', 'expected'), [
    ('the united states', 'united states', True),
    ('the united states of america', 'united states', False),
    ('brlin', 'berlin', True),
    ('Warsaw', 'warsaw', True),
    ('Western Europe', 'Europe', False),
    ('Europ', 'Europe', True),
    ('Pakistan', 'Iceland', False),
    ('United States', 'United Arab Emirates', False),
])
def test_fuzzy_match(name, option, expected):
    assert fuzzy_match(name.lower(), option.lower()) is expected
