LocationExtractor
========
[![Build Status](https://travis-ci.com/MMatlacz/LocationExtractor.svg?token=nK1H37yHzQmBRmsEpSZq&branch=master)](https://travis-ci.com/MMatlacz/LocationExtractor)
[![codecov](https://codecov.io/gh/MMatlacz/LocationExtractor/branch/master/graph/badge.svg)](https://codecov.io/gh/MMatlacz/LocationExtractor)

Extract place names from a URL or text, and add context to those names -- for 
example distinguishing between a country, region or city. 

## Install & Setup

Grab the package using `pip` (this will take a few minutes)

    package not yet availabe on pypi

## Basic Usage

Import the module, give some text or a URL, and presto.

    TODO

## Credits

LocationExtractor is based on:

* [geograpy](https://github.com/ushahidi/geograpy)

LocationExtractor uses the following excellent libraries:

* [NLTK](http://www.nltk.org/) for entity recognition
* [newspaper](https://github.com/codelucas/newspaper) for text extraction from HTML
* [jellyfish](https://github.com/sunlightlabs/jellyfish) for fuzzy text match
* [pycountry](https://pypi.python.org/pypi/pycountry) for country/region lookups

LocationExtractor uses the following data sources:
* This product includes GeoLite2 data created by MaxMind, available from <a href="https://www.maxmind.com">https://www.maxmind.com</a>
* [ISO3166ErrorDictionary](https://github.com/bodacea/countryname/blob/master/countryname/databases/ISO3166ErrorDictionary.csv) for common country mispellings _via [Sara-Jayne Terp](https://github.com/bodacea)_
