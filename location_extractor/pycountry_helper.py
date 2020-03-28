import os

from typing import Optional

import pandas as pd
import pycountry

from location_extractor import src_dir
from location_extractor.containers import Country, Region


class PycountryHelper:
    def __init__(self):
        dictionary = pd.read_csv(os.path.join(src_dir, "data", "ISO3166ErrorDictionary.csv"))
        self.dictionary = dict(zip(*dictionary[["data.un.org entry", "ISO3166 name or code"]].values.T))

    def get_field(self, country_object: pycountry.db.Data, field_name: str) -> str:
        fields = country_object.__dict__['_fields']
        value = fields.get(field_name)
        return value

    def get_country_name_and_iso_code(self, country_name: str) -> Optional[Country]:
        cleaned_name = self.dictionary.get(country_name, country_name)
        try:
            country_object = pycountry.countries.get(name=cleaned_name)
        except KeyError:
            country_object = None
        except LookupError:
            country_object = None

        if not country_object:
            try:
                country_object = pycountry.countries.search_fuzzy(cleaned_name)
            except LookupError:
                pass

        if isinstance(country_object, list):
            for found_country in country_object:
                name = self.get_field(found_country, 'name')
                official_name = self.get_field(found_country, 'official_name')
                alpha_2 = self.get_field(found_country, 'alpha_2')

                if name and (cleaned_name in {name, official_name}):
                    return Country(name=name, iso_code=alpha_2)
                elif name and cleaned_name in name.split():
                    return Country(name=name, iso_code=alpha_2)
        elif isinstance(country_object, pycountry.db.Data):
            return Country(name=country_object.name, iso_code=country_object.alpha_2)
        else:
            return None

    def get_region_names(self, country: Country):
        try:
            country_object = pycountry.countries.get(name=country.name)
            regions = pycountry.subdivisions.get(country_code=country_object.alpha_2)
        except KeyError:
            return []
        except AttributeError:
            return []

        return [Region(name=region.name, country=country) for region in regions]
