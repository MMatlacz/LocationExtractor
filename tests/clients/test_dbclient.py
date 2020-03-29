import operator
import os
import sqlite3

import pytest

from location_extractor.clients import LocationDTO


def test_populate_locations_table(dbclient):
    if os.path.exists(dbclient.dbpath):
        os.remove(dbclient.dbpath)

    with pytest.raises(
        sqlite3.DatabaseError,
        match='no such table: locations',
    ):
        dbclient.fetch_all_raw('country_name', 'Spain', 'country_name')

    dbclient.populate_locations_table()

    countries = dbclient.fetch_all_raw(  # noqa: WPS317
        'country_name',
        ('Spain', 'France'),
        'country_name',
    )
    assert len(countries) == 2
    assert tuple(map(len, countries)) == (1, 1)
    assert (
        sorted(map(operator.itemgetter(0), countries)) == ['France', 'Spain']
    )


def test_fetch_all_raw(dbclient):
    country = dbclient.fetch_one_raw(  # noqa: WPS317
        'country_name',
        'Paraguay',
        ('country_name', 'continent_name'),
    )
    assert len(country) == 2
    assert country == ('Paraguay', 'South America')


def test_fetch_one(dbclient):
    country = dbclient.fetch_one('continent_name', 'Asia')
    assert isinstance(country, LocationDTO)
    assert country.continent_name == 'Asia'
