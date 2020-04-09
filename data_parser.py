import requests
import csv
from io import StringIO
from functools import lru_cache

class Country:
    def __init__(self, name, population_count, time_series):
        self.name = name
        self.population_count = population_count
        self.time_series = time_series
        self.confirmed = {time:data[0] for time, data in self.time_series.items()}
        self.recovered = {time:data[1] for time, data in self.time_series.items()}
        self.deaths = {time:data[2] for time, data in self.time_series.items()}


class Database:

    def __init__(self):
        # Get covid data
        r = requests.get('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv')
        raw_data = StringIO(r.text)
        reader = csv.reader(raw_data, delimiter=',')

        covid_data = {}
        for index, row in enumerate(reader, start=0):
            if index == 0:
                continue
            if row[1] not in covid_data:
                covid_data[row[1]] = {}

            covid_data[row[1]][row[0]] = row[2:]

        # Get countries population count
        r = requests.get('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv')
        raw_data = StringIO(r.text)
        reader = csv.reader(raw_data, delimiter=',')

        population_per_country = {}
        for index, row in enumerate(reader, start=0):
            if index == 0 or row[6] != "":
                continue
            if row[7] not in population_per_country:
                population_per_country[row[7]] = row[11]

        for country, pop in population_per_country.items():
            if country not in covid_data:
                print(f"Error: {country} has no covid statistics !")

        self.countries = {country:Country(country, population_per_country[country], time_series) for country, time_series in covid_data.items()}



db = Database()
