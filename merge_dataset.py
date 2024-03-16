import pandas as pd
from math import radians, cos, sin, asin, sqrt


def merge_lat_lon():
    europe_airports = pd.read_csv('europe_airports.csv')
    europe_routes = pd.read_csv('europe_routes.csv')

    # Merge the merged data with Europe data on Source airport
    merged_data = pd.merge(europe_routes, europe_airports[['IATA', 'Latitude', 'Longitude']], how='left',
                           left_on='Source airport', right_on='IATA')

    # Drop the redundant 'IATA' column
    merged_data.drop(columns=['IATA'], inplace=True)

    # Merge the merged data with Europe data on Destination airport
    merged_data = pd.merge(merged_data, europe_airports[['IATA', 'Latitude', 'Longitude']], how='left',
                           left_on='Destination airport', right_on='IATA', suffixes=('_source', '_destination'))

    # Drop the redundant 'IATA' column
    merged_data.drop(columns=['IATA'], inplace=True)
    print(merged_data)
    merged_data.to_csv("europe_flights_without_distance.csv", index=False)


def haversine_formula_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # radius of earth in kilometers
    return c * r


def main():
    data = pd.read_csv("europe_flights_without_distance.csv")
    data.columns = ["Airline", "Airline ID", "Source airport", "Destination airport",
                    "Source Latitude", "Source Longitude",
                    "Destination Latitude", "Destination Longitude"]
    data['Distance'] = data.apply(
        lambda row: haversine_formula_distance(row['Source Latitude'], row['Source Longitude'],
                                               row['Destination Latitude'], row['Destination Longitude']), axis=1)

    data.to_csv("europe_flight_dataset.csv", index=False)


if __name__ == "__main__":
    merge_lat_lon()
    main()
