import os

import pandas as pd
from unidecode import unidecode_expect_nonascii

from location_extractor import src_dir


def load_locations() -> pd.DataFrame:
    locations_path = os.path.join(
        src_dir, "data", "GeoLite2-City-CSV_20200303", "GeoLite2-City-Locations-en.csv")
    city_locations = pd.read_csv(
        locations_path,
        dtype={
            'geoname_id': int,
            'continent_code': 'string',
            'continent_name': 'string',
            'country_iso_code': 'string',
            'country_name': 'string',
            'subdivision_1_name': 'string',
            'subdivision_2_name': 'string',
            'city_name': 'string',
            'metro_code': 'string',
            'time_zone': 'string',
            'is_in_european_union': bool
        }
    )

    subdivision1 = city_locations.copy() \
        .drop(columns=['subdivision_2_name']) \
        .rename(columns={'subdivision_1_name': 'subdivision_name'}) \
        .dropna(subset=['subdivision_name'])
    subdivision2 = city_locations.copy() \
        .drop(columns=['subdivision_1_name']) \
        .rename(columns={'subdivision_2_name': 'subdivision_name'}) \
        .dropna(subset=['subdivision_name'])

    city_locations = subdivision1.append(subdivision2)

    city_locations.drop(columns=[
        'geoname_id',
        'subdivision_1_iso_code',
        'subdivision_2_iso_code',
        'metro_code',
        'time_zone'],
        inplace=True
    )

    city_locations.fillna(
        value={
            'geoname_id': -1,
            'continent_code': '',
            'continent_name': '',
            'country_iso_code': '',
            'country_name': '',
            'subdivision_name': '',
            'city_name': '',
            'metro_code': '',
            'time_zone': ''
        },
        inplace=True
    )

    city_locations["country_name"] = city_locations["country_name"].map(unidecode_expect_nonascii)
    city_locations["subdivision_name"] = city_locations["subdivision_name"].map(unidecode_expect_nonascii)
    city_locations["city_name"] = city_locations["city_name"].map(unidecode_expect_nonascii)

    city_locations = city_locations.astype(
        {
            'locale_code': 'string',
            'continent_code': 'string',
            'continent_name': 'string',
            'country_iso_code': 'string',
            'country_name': 'string',
            'subdivision_name': 'string',
            'city_name': 'string',
            'is_in_european_union': bool
        },
        copy=False
    )

    return city_locations


if __name__ == "__main__":
    save_location = locations_path = os.path.join(
        src_dir, "data", "GeoLite2-City-CSV_20200303", "GeoLite2-City-Locations-en-processed.csv")
    locations = load_locations()
    locations.to_csv(save_location, index=False)
