import os
import sqlite3
from dataclasses import dataclass
from sqlite3 import Cursor, Connection
from typing import List, Tuple, Union, Optional

from location_extractor import src_dir
from location_extractor.helpers import remove_accents
import csv


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

                locations_data = []
                with open(locations_path, 'r') as locations_file:
                    reader = csv.reader(locations_file, delimiter=',')
                    columns = next(reader)
                    for i in range(len(columns) - 1):
                        columns.append(f'{col}_lowercase')

                    for row in reader:
                        locale_code = row[0] or ''
                        continent_code = row[1] or ''
                        continent_name = row[2] or ''
                        country_iso_code = row[3] or ''
                        country_name = row[4] or ''
                        subdivision_name = row[5] or ''
                        city_name = row[6] or ''
                        is_in_european_union = True if row[7] == 'True' else False
                        locations_data.append((
                            locale_code,
                            continent_code,
                            continent_name,
                            country_iso_code,
                            country_name,
                            subdivision_name,
                            city_name,
                            is_in_european_union,
                            locale_code.lower(),
                            continent_code.lower(),
                            continent_name.lower(),
                            country_iso_code.lower(),
                            country_name.lower(),
                            subdivision_name.lower(),
                            city_name.lower(),
                        ))

                conn.executemany(
                    '''
                        INSERT INTO locations 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ''',
                    locations_data
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
        with self.connect() as conn:  # type: Connection
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
