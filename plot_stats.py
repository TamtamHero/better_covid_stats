from data_parser import Database
from nvd3 import lineWithFocusChart, linePlusBarChart


def plot_from_date_when_threshold_is_reached(db, data_name, num_country=10, threshold=0, min_pop=1000000, min_confirmed_case=2000, forced_countries=[]):
    chart = lineWithFocusChart(name='lineWithFocusChart', x_is_date=True, x_axis_format="%d %b %Y", width=1750,
                               height=900)

    xdata = db.timestamps
    sorted_countries = db.countries
    sorted_countries.sort(key=lambda country: getattr(country, data_name)[-1], reverse=True)

    for index, country in enumerate(sorted_countries):
        if (index > num_country or country.population_count < min_pop or country.confirmed_case[-1] < min_confirmed_case) and country.name not in forced_countries:
            continue
        ydata = [ count for count in getattr(country, data_name) if count >= threshold]
        if ydata == []:
            break

        extra_serie = {"tooltip": {"y_start": "", "y_end": " ext"},
                       "date_format": "%d %b %Y", "size": 15}
        chart.add_serie(name=country.name, y=ydata, x=xdata, extra=extra_serie)

    chart.buildhtml()

    with open(f"plot_{data_name}_from_date_when_{threshold}_is_reached.html", 'w') as f:
        f.write(chart.htmlcontent)


def plot_single_country_with_bars(db, country_name, line_data_name, bar_data_name):
    chart = linePlusBarChart(name='lineWithFocusChart', x_is_date=True, x_axis_format="%d %b %Y", width=1750,
                               height=900, focus_enable=True, yaxis2_format="function(d) { return d3.format(',0.3f')(d) }")

    xdata = db.timestamps
    country = db.countries_dict[country_name]

    ydata_line = [ y for y in getattr(country, line_data_name)]
    ydata_bar = [ y for y in getattr(country, bar_data_name)]

    extra_serie = {"tooltip": {"y_start": "", "y_end": " ext"},
                   "date_format": "%d %b %Y", "size": 15}

    chart.add_serie(name=f"{line_data_name} in {country.name}", y=ydata_line, x=xdata, extra=extra_serie)
    chart.add_serie(name=f"{bar_data_name} in {country.name}", y=ydata_bar, x=xdata, extra=extra_serie, bar=True)

    chart.buildhtml()

    with open(f"plot_{line_data_name}_with_{bar_data_name}_as_bars_for_{country_name}.html", 'w') as f:
        f.write(chart.htmlcontent)


if __name__ == "__main__":
    db = Database()
    plot_from_date_when_threshold_is_reached(db, "deaths_per_1m", num_country=20, threshold=0)
    plot_from_date_when_threshold_is_reached(db, "deaths_per_1m", num_country=20, threshold=40)
    plot_from_date_when_threshold_is_reached(db, "confirmed_case_per_1m", num_country=20, threshold=40)
    plot_from_date_when_threshold_is_reached(db, "death_per_detected_case_percentage_evolution", num_country=20, threshold=0.01)
    plot_from_date_when_threshold_is_reached(db, "death_per_detected_case_percentage_evolution", num_country=20, forced_countries=["Germany", "US"])


    plot_single_country_with_bars(db, "Germany", "death_per_detected_case_percentage_evolution", "confirmed_case_per_1m")
    plot_single_country_with_bars(db, "US", "death_per_detected_case_percentage_evolution", "confirmed_case_per_1m")
    plot_single_country_with_bars(db, "France", "death_per_detected_case_percentage_evolution", "confirmed_case_per_1m")

