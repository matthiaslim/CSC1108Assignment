import os
from processing import data_merging, csv_operations
from utils import flight_analysis
import pandas as pd


def slice_airport_data(airports, criteria):
    sliced_airports = []
    for airport in airports:
        # append rows based on criteria and do not append air bases (RAF = Royal Air Force)
        if criteria(airport) and 'airbase' not in airport['Name'].lower() and 'air base' not in airport[
                'Name'].lower() and 'RAF' not in airport['Name']:
            sliced_airports.append(airport)
    return sliced_airports


def criteria_function(airport):
    # Criteria for this dataset: Europe and not in Russia, must also have existing IATA
    return 'Europe' in airport['Tz database time zone'] and airport['Country'] != 'Russia' and airport['IATA'] != '\\N'


def slice_routes_data(airports, routes):
    sliced_routes = []
    europe_airports = [airport['IATA'] for airport in airports]
    for route in routes:
        if route['Source airport'] in europe_airports and route['Destination airport'] in europe_airports:
            sliced_routes.append(route)
            # Drop unwanted columns before appending
            del route['Airline']
            del route['Airline ID']
    return sliced_routes


def main():
    # Get the directory path of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Define the directory path for the data folder
    data_directory = os.path.join(current_directory, '..', 'data')

    # Read airports data
    airports = csv_operations.read_csv(os.path.join(data_directory, 'airports.csv'))

    # Slice airport data
    sliced_airports = slice_airport_data(airports, criteria_function)

    # Write sliced airports data to CSV
    csv_operations.write_to_csv(sliced_airports, os.path.join(data_directory, 'europe_airports.csv'),
                                columns=['Name', 'City', 'Country', 'IATA', 'Latitude', 'Longitude',
                                         'Altitude', 'Timezone', 'DST'])

    # Read routes data
    routes = csv_operations.read_csv('../data/routes.csv')

    # Slice routes data
    sliced_routes = slice_routes_data(sliced_airports, routes)

    # Write sliced routes data to CSV
    csv_operations.write_to_csv(sliced_routes, os.path.join(data_directory, 'europe_routes.csv'),
                                columns=['Source airport', 'Destination airport'])

    # Merge city-country data
    europe_airports = pd.read_csv(os.path.join(data_directory, 'europe_airports.csv'))
    europe_routes = pd.read_csv(os.path.join(data_directory, 'europe_routes.csv'))
    modified_europe_routes = data_merging.merge_city_country(europe_airports, europe_routes)

    # Merge latitude-longitude data
    data_merging.merge_lat_lon(europe_airports, modified_europe_routes)

    # Calculate flight distance
    flight_analysis.calculate_distance()

    # Calculate flight cost
    flight_analysis.calculate_cost()

    # Calculate flight duration
    flight_analysis.calculate_duration()


if __name__ == "__main__":
    main()
