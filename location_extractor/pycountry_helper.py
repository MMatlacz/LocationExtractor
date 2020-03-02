from typing import Optional, Tuple

import pycountry

from location_extractor.containers import Country, Region


class PycountryHelper:
    def get_field(self, country_object: pycountry.db.Data, field_name: str) -> str:
        fields = country_object.__dict__['_fields']
        value = fields.get(field_name)
        return value

    def get_country_name_and_iso_code(self, country: str) -> Optional[Country]:
        try:
            country_object = pycountry.countries.get(name=country)
        except KeyError:
            country_object = None
        except LookupError:
            country_object = None

        if not country_object:
            try:
                country_object = pycountry.countries.search_fuzzy(country)
            except LookupError:
                pass

        if isinstance(country_object, list):
            for found_country in country_object:
                name = self.get_field(found_country, 'name')
                official_name = self.get_field(found_country, 'official_name')
                alpha_3 = self.get_field(found_country, 'alpha_3')
                alpha_2 = self.get_field(found_country, 'alpha_2')

                if name and (country in {name, official_name, alpha_3, alpha_2}):
                    return Country(name=name, iso_code=alpha_2)
                elif name and country in name:
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
