import requests
import csv
from io import StringIO
from functools import lru_cache
import time
import datetime

class Country:
    def __init__(self, name, population_count, time_series):
        self.name = name
        self.population_count = int(population_count)
        self.time = list(time_series.keys())

        # raw data
        self.confirmed_case = [int(data[0]) for time, data in time_series.items()]
        self.recovered = [int(data[1] )for time, data in time_series.items()]
        self.deaths = [int(data[2]) for time, data in time_series.items()]

        # data per capita
        coeff = self.population_count/1000000
        self.confirmed_case_per_1m = [round(count / coeff) for count in self.confirmed_case]
        self.recovered_per_1m = [round(count / coeff) for count in self.recovered]
        self.deaths_per_1m = [round(count / coeff) for count in self.deaths]

        # combined data
        self.death_per_detected_case_percentage_evolution = [round((deaths / confirmed_case) * 100, 2) if deaths > 0 else 0 for deaths, confirmed_case in zip(self.deaths, self.confirmed_case)]

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
            if row[7] not in population_per_country and row[11]:
                population_per_country[row[7]] = row[11]

        places_that_are_not_countries = []
        for country, data in covid_data.items():
            if country not in population_per_country:
                places_that_are_not_countries += [country]

        for c in places_that_are_not_countries:
            del covid_data[c]

        self.countries = [Country(country, population_per_country[country], time_series) for country, time_series in covid_data.items()]
        self.countries_dict = {country.name:country for country in self.countries}
        self.time = list(covid_data["US"].keys())
        self.timestamps = [time.mktime(datetime.datetime.strptime(t, "%Y-%m-%d").timetuple())*1000 for t in self.time]


def build_global_death_per_1m_csv(db, timestamp=True):

    with open("global_death_per_1m.csv", 'w') as output_file:
        out = csv.writer(output_file)
        out.writerow(['time'] + db.time)
        for country in db.countries:
            out.writerow([country.name] + list(country.deaths_per_1m))


if __name__ == "__main__":
    db = Database()
    build_global_death_per_1m_csv(db)