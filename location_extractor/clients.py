import csv
import os
import sqlite3

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple, Union

from typing_extensions import Final

from location_extractor import src_dir
from location_extractor.utils import remove_accents

StringOrIterableOfStrings = Union[str, Iterable[str]]
COMMA: Final = ','
LOWERCASE_COLUMN_SUFFIX: Final = '_lowercase'


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


# TODO: refactor ``DBClient`` to have lower complexity and amount of methods
class DBClient:  # noqa: WPS214
    def __init__(self) -> None:
        self.dbpath = os.path.join(src_dir, 'data', 'data.db')
        self.locations_path = os.path.join(
            src_dir,
            'data',
            'GeoLite2-City-CSV_20200303',
            'GeoLite2-City-Locations-en-processed.csv',
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
        self.columns = COMMA.join(self.default_columns)
        self.populate_locations_table()

    @property
    def connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.dbpath)

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
                self._create_locations_table(conn)
                self._populate_locations_table_with_data(conn)

    @staticmethod
    def parse_values(
        value: StringOrIterableOfStrings,
    ) -> StringOrIterableOfStrings:
        if isinstance(value, str):
            value = remove_accents(value.lower())
        else:
            value = [remove_accents(str_value.lower()) for str_value in value]
        return value

    def parse_columns(
        self,
        columns: Optional[StringOrIterableOfStrings],
    ) -> StringOrIterableOfStrings:
        # TODO: refactor this conditions to get rid of below ignored violation
        if not columns:  # noqa: WPS504
            selected_columns = self.columns
        elif isinstance(columns, str):
            selected_columns = columns
        else:
            selected_columns = COMMA.join(columns)
        return selected_columns

    @staticmethod
    def query(
        column_name: str,
        columns: str,
        conn: sqlite3.Connection,
        value: str,
    ) -> sqlite3.Cursor:
        return conn.execute(
            f'''
                SELECT DISTINCT
                    {columns}
                FROM
                    locations
                WHERE
                    {column_name}=?
            ''',
            (value,),
        )

    @staticmethod
    def query_in(
        column_name: str,
        columns: str,
        conn: sqlite3.Connection,
        value: List[str],
    ) -> sqlite3.Cursor:
        return conn.execute(
            f'''
                SELECT DISTINCT
                    {columns}
                FROM
                    locations
                WHERE
                    {column_name} IN ({COMMA.join('?' * len(value))})
            ''',
            value,
        )

    def fetch_all_raw(
        self,
        column_name: str,
        value: StringOrIterableOfStrings,
        columns: Optional[StringOrIterableOfStrings] = None,
    ) -> List[Tuple]:
        with self.connection as conn:
            value = self.parse_values(value)
            columns = self.parse_columns(columns)
            column_name = f'{column_name}{LOWERCASE_COLUMN_SUFFIX}'
            if isinstance(value, str):
                cursor = self.query(column_name, columns, conn, value)
            else:
                cursor = self.query_in(column_name, columns, conn, value)
            return cursor.fetchall()

    def fetch_all(
        self,
        column_name: str,
        value: StringOrIterableOfStrings,
    ) -> List[LocationDTO]:
        with self.connection as conn:
            value = self.parse_values(value)
            column_name = f'{column_name}{LOWERCASE_COLUMN_SUFFIX}'
            if isinstance(value, str):
                cursor = self.query(column_name, self.columns, conn, value)
            else:
                cursor = self.query_in(column_name, self.columns, conn, value)
            records = cursor.fetchall()
            return [LocationDTO(*record) for record in records]

    def fetch_one_raw(
        self,
        column_name: str,
        value: str,
        columns: Optional[Union[StringOrIterableOfStrings]] = None,
    ) -> Optional[Tuple]:
        with self.connection as conn:
            value = self.parse_values(value)
            columns = self.parse_columns(columns)
            column_name = f'{column_name}{LOWERCASE_COLUMN_SUFFIX}'
            cursor = self.query(column_name, columns, conn, value)
            return cursor.fetchone()

    def fetch_one(self, column_name: str, value: str) -> Optional[LocationDTO]:
        with self.connection as conn:
            if isinstance(value, str):
                value = remove_accents(value.lower())
            column_name = f'{column_name}{LOWERCASE_COLUMN_SUFFIX}'
            cursor = self.query(column_name, self.columns, conn, value)
            records: Tuple = cursor.fetchone()
            return LocationDTO(*records) if records else None

    def _create_locations_table(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            f'''
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
                    locale_code{LOWERCASE_COLUMN_SUFFIX} text,
                    continent_code{LOWERCASE_COLUMN_SUFFIX} text,
                    continent_name{LOWERCASE_COLUMN_SUFFIX} text,
                    country_iso_code{LOWERCASE_COLUMN_SUFFIX} text,
                    country_name{LOWERCASE_COLUMN_SUFFIX} text,
                    subdivision_name{LOWERCASE_COLUMN_SUFFIX} text,
                    city_name{LOWERCASE_COLUMN_SUFFIX} text
                )
            ''',
        )

        for column_name in self.index_columns:
            connection.execute(
                f'''
                    CREATE INDEX {column_name}
                    ON locations({column_name}{LOWERCASE_COLUMN_SUFFIX});
                ''',
            )

    # TODO: refactor ``_populate_locations_table_with_data`` to have
    # lower amount of variables
    def _populate_locations_table_with_data(  # noqa: WPS210
        self,
        connection: sqlite3.Connection,
    ) -> None:
        locations_data = []
        with open(self.locations_path, 'r') as locations_file:
            reader = csv.reader(locations_file, delimiter=COMMA)
            columns = list(next(reader))
            columns = [
                *columns,
                *(
                    f'{column_name}{LOWERCASE_COLUMN_SUFFIX}'
                    for column_name in columns[:-1]
                ),
            ]
            for row in reader:
                str_values = [value or '' for value in row[:7]]
                locations_data.append((
                    *str_values,
                    row[7] == 'True',  # is_in_european_union,
                    *(value.lower() for value in str_values),
                ))

        connection.executemany(
            '''
                INSERT INTO locations
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''',
            locations_data,
        )
