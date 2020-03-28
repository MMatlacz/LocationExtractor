import os
import sqlite3
from dataclasses import dataclass
from sqlite3 import Cursor
from typing import List, Tuple, Union, Optional

import pandas as pd

from location_extractor import src_dir
from location_extractor.helpers import remove_accents


@dataclass(frozen=True, order=True)
class LocationDTO:
    locale_code: str
    continent_code: str
    continent_name: str
    country_iso_code: str
    country_name: str
    subdivision_name: str
    city_name: str
    is_in_european_union: bool


class DBClient:
    def __init__(self) -> None:
        self.dbpath = os.path.join(src_dir, "data", "data.db")

        self.index_columns = [
            'continent_name',
            'country_iso_code',
            'country_name',
            'subdivision_name',
            'city_name',
        ]

        with self.connect() as conn:
            table_exists = conn.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='locations';
            """).fetchone()

            if not table_exists:
                conn.execute('''
                    CREATE TABLE locations
                    (
                        locale_code text,
                        continent_code text,
                        continent_name text,
                        country_iso_code text,
                        country_name text,
                        subdivision_name text,
                        city_name text,
                        is_in_european_union boolean,
                        locale_code_lowercase text,
                        continent_code_lowercase text,
                        continent_name_lowercase text,
                        country_iso_code_lowercase text,
                        country_name_lowercase text,
                        subdivision_name_lowercase text,
                        city_name_lowercase text
                    )
                    ''')

                for col in self.index_columns:
                    conn.execute(f'''
                        CREATE INDEX {col} 
                        ON locations({col}_lowercase);
                    ''')

                locations_path = os.path.join(
                    src_dir, "data", "GeoLite2-City-CSV_20200303", "GeoLite2-City-Locations-en-processed.csv")
                locations_data: pd.DataFrame = pd.read_csv(
                    locations_path,
                    dtype={
                        'locale_code': 'string',
                        'continent_code': 'string',
                        'continent_name': 'string',
                        'country_iso_code': 'string',
                        'country_name': 'string',
                        'subdivision_name': 'string',
                        'city_name': 'string',
                        'is_in_european_union': 'bool'
                    }
                )

                for col in locations_data.select_dtypes(include=['object', 'string']):
                    locations_data[col].fillna('', inplace=True)
                    locations_data[f'{col}_lowercase'] = locations_data[col].str.lower()

                for row in locations_data.itertuples(index=False, name=None):
                    conn.execute(
                        '''
                            INSERT INTO locations 
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        ''',
                        row
                    )

        self.default_columns = [
            'locale_code',
            'continent_code',
            'continent_name',
            'country_iso_code',
            'country_name',
            'subdivision_name',
            'city_name',
            'is_in_european_union',
        ]

        self.columns = ','.join(self.default_columns)

    def connect(self):
        return sqlite3.connect(self.dbpath)

    def fetch_all_raw(self, column_name: str, value: Union[str, List[str]],
                      columns: Union[List[str], str] = None) -> List[Tuple]:
        with self.connect() as conn:
            if isinstance(value, str):
                value = remove_accents(value.lower())
            else:
                value = [remove_accents(val.lower()) for val in value]

            if not columns:
                selected_columns = self.columns
            elif isinstance(columns, str):
                selected_columns = columns
            else:
                selected_columns = ','.join(columns)

            column_name = f'{column_name}_lowercase'
            if isinstance(value, str):
                cursor: Cursor = conn.execute(
                    f'''
                        SELECT DISTINCT {selected_columns} FROM 
                            locations 
                        WHERE 
                            {column_name}=?
                    ''',
                    (value,)
                )
            else:
                cursor: Cursor = conn.execute(
                    f'''
                        SELECT DISTINCT {selected_columns} FROM 
                            locations 
                        WHERE 
                            {column_name} IN ({",".join("?" * len(value))})
                    ''',
                    value
                )

            records = cursor.fetchall()
            return records

    def fetch_all(self, column_name: str, value: Union[str, List[str]]) -> List[LocationDTO]:
        with self.connect() as conn:
            if isinstance(value, str):
                value = remove_accents(value.lower())
            else:
                value = [remove_accents(val.lower()) for val in value]

            column_name = f'{column_name}_lowercase'
            if isinstance(value, str):
                cursor: Cursor = conn.execute(
                    f'''
                        SELECT {self.columns} FROM 
                            locations 
                        WHERE 
                            {column_name}=?
                    ''',
                    (value,)
                )
            else:
                cursor: Cursor = conn.execute(
                    f'''
                        SELECT {self.columns} FROM 
                            locations 
                        WHERE 
                            {column_name} IN ({",".join("?" * len(value))})
                    ''',
                    value
                )

            records = cursor.fetchall()
            return [LocationDTO(*record) for record in records]

    def fetch_one_raw(self, column_name: str, value: str,
                      columns: Optional[Union[List[str], str]] = None) -> Optional[Tuple]:
        with self.connect() as conn:
            if isinstance(value, str):
                value = remove_accents(value.lower())

            if columns and isinstance(columns, list):
                columns = ",".join(columns)
            elif not columns:
                columns = self.columns

            column_name = f'{column_name}_lowercase'

            cursor: Cursor = conn.execute(
                f'''
                    SELECT DISTINCT {columns} FROM 
                        locations 
                    WHERE 
                        {column_name}=?
                ''',
                (value,)
            )

            records = cursor.fetchone()
            if records:
                return records
            else:
                return None

    def fetch_one(self, column_name: str, value: str) -> Optional[LocationDTO]:
        with self.connect() as conn:
            if isinstance(value, str):
                value = remove_accents(value.lower())

            column_name = f'{column_name}_lowercase'

            cursor: Cursor = conn.execute(
                f'''
                    SELECT DISTINCT {self.columns} FROM 
                        locations 
                    WHERE 
                        {column_name}=?
                ''',
                (value,)
            )

            records: Tuple = cursor.fetchone()
            if records:
                return LocationDTO(*records)
            else:
                return None
