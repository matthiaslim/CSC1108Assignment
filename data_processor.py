import csv


def read_airport_data(file_path):
    airports = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        for row in csv.DictReader(csvfile):
            airports.append(row)
    return airports


def slice_airport_data(airports, criteria):
    sliced_airports = []
    for airport in airports:
        if criteria(airport):
            sliced_airports.append(airport)
    return sliced_airports


def criteria_function(airport):
    # Criteria for this dataset: Europe and not in Russia, must also have existing IATA
    return 'Europe' in airport['Tz database time zone'] and airport['Country'] != 'Russia' and airport['IATA'] != '\\N'


def write_to_csv(data, file_path, columns):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        if columns:
            fieldnames = columns  # Assuming all dictionaries have the same keys
        else:
            fieldnames = data[0].keys()

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)


def read_routes_data(file_path):
    routes = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        for row in csv.DictReader(csvfile):
            routes.append(row)

    return routes


def slice_routes_data(airports, routes):
    sliced_routes = []
    europe_airports = [airport['IATA'] for airport in airports]
    for route in routes:
        if route['Source airport'] in europe_airports and route['Destination airport'] in europe_airports:
            sliced_routes.append(route)
    return sliced_routes


def main():
    # read the airports data
    airports_file = 'airports.csv'
    airports = read_airport_data(airports_file)

    # read the routes data
    routes_file = 'routes.csv'
    routes = read_routes_data(routes_file)

    # Slice the airport data based on criteria
    sliced_airports = slice_airport_data(airports, criteria_function)
    # Specify headers to append to airport dataset
    data_to_append_airports = ['Name', 'City', 'Country', 'IATA', 'Latitude', 'Longitude', 'Altitude', 'Timezone',
                               'DST']
    write_to_csv(sliced_airports, 'europe_airports.csv', data_to_append_airports)

    # Slice the routes data after comparing the IATA with airport data
    sliced_routes = slice_routes_data(sliced_airports, routes)
    data_to_append_routes = ['Airline', 'Airline ID', 'Source airport', 'Destination airport']
    write_to_csv(sliced_routes, 'europe_routes.csv', data_to_append_routes)


if __name__ == "__main__":
    main()
