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
    dbpath = os.path.join(src_dir, 'data', 'data.db')

    def __init__(self) -> None:
        self.locations_path = os.path.join(
            src_dir,
            'data',
            'GeoLite2-City-CSV_20200303',
            'GeoLite2-City-Locations-en-processed.csv'
        )

        self.index_columns = (
            'continent_name',
            'country_iso_code',
            'country_name',
            'subdivision_name',
            'city_name',
        )

        self.default_columns = (
            'locale_code',
            'continent_code',
            'continent_name',
            'country_iso_code',
            'country_name',
            'subdivision_name',
            'city_name',
            'is_in_european_union',
        )

        self.columns = ','.join(self.default_columns)

        self.populate_locations_table()

    def populate_locations_table(self) -> None:
        with self.connection as conn:
            table_exists = conn.execute('''
                SELECT 
                    name 
                FROM 
                    sqlite_master 
                WHERE 
                    type='table' AND name='locations';
            ''').fetchone()

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
                    column_name = f'{col}_lowercase'
                    conn.execute(f'CREATE INDEX {col} ON locations({column_name});')

                locations_data = []
                with open(self.locations_path, 'r') as locations_file:
                    reader = csv.reader(locations_file, delimiter=',')
                    columns = next(reader)
                    for col in self.default_columns[:7]:
                        columns.append(f'{col}_lowercase')

                    for row in reader:
                        str_values = [value or '' for value in row[:7]]
                        is_in_european_union = True if row[7] == 'True' else False
                        locations_data.append((
                            *str_values,
                            is_in_european_union,
                            *(value.lower() for value in str_values)
                        ))

                conn.executemany(
                    'INSERT INTO locations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    locations_data
                )

    @property
    def connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.dbpath)

    @staticmethod
    def parse_values(value: Union[str, List[str]]) -> Union[str, List[str]]:
        if isinstance(value, str):
            value = remove_accents(value.lower())
        else:
            value = [remove_accents(val.lower()) for val in value]
        return value

    def parse_columns(self, columns):
        if not columns:
            selected_columns = self.columns
        elif isinstance(columns, str):
            selected_columns = columns
        else:
            selected_columns = ','.join(columns)
        return selected_columns

    @staticmethod
    def query(column_name: str, columns: str, conn: sqlite3.Connection, value: str):
        cursor: Cursor = conn.execute(
            f'''
                        SELECT DISTINCT 
                            {columns} 
                        FROM 
                            locations 
                        WHERE 
                            {column_name}=?
                    ''',
            (value,)
        )
        return cursor

    @staticmethod
    def query_in(column_name: str, columns: str, conn: sqlite3.Connection, value: List[str]):
        cursor: Cursor = conn.execute(
            f'''
                        SELECT DISTINCT 
                            {columns} 
                        FROM 
                            locations 
                        WHERE 
                            {column_name} IN ({','.join('?' * len(value))})
                    ''',
            value
        )
        return cursor

    def fetch_all_raw(self, column_name: str, value: Union[str, List[str]],
                      columns: Union[List[str], str] = None) -> List[Tuple]:
        with self.connection as conn:  # type: Connection
            value = self.parse_values(value)
            columns = self.parse_columns(columns)

            column_name = f'{column_name}_lowercase'
            if isinstance(value, str):
                cursor = self.query(column_name, columns, conn, value)
            else:
                cursor = self.query_in(column_name, columns, conn, value)

            records = cursor.fetchall()
            return records

    def fetch_all(self, column_name: str, value: Union[str, List[str]]) -> List[LocationDTO]:
        with self.connection as conn:
            value = self.parse_values(value)

            column_name = f'{column_name}_lowercase'
            if isinstance(value, str):
                cursor = self.query(column_name, self.columns, conn, value)
            else:
                cursor = self.query_in(column_name, self.columns, conn, value)

            records = cursor.fetchall()
            return [LocationDTO(*record) for record in records]

    def fetch_one_raw(self, column_name: str, value: str,
                      columns: Optional[Union[List[str], str]] = None) -> Optional[Tuple]:
        with self.connection as conn:
            value = self.parse_values(value)
            columns = self.parse_columns(columns)

            column_name = f'{column_name}_lowercase'
            cursor = self.query(column_name, columns, conn, value)

            records = cursor.fetchone()
            return records

    def fetch_one(self, column_name: str, value: str) -> Optional[LocationDTO]:
        with self.connection as conn:
            if isinstance(value, str):
                value = remove_accents(value.lower())

            column_name = f'{column_name}_lowercase'
            cursor = self.query(column_name, self.columns, conn, value)

            records: Tuple = cursor.fetchone()
            return LocationDTO(*records) if records else None
