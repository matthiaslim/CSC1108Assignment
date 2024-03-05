import pandas as pd
from math import radians, cos, sin, asin, sqrt


def merge_lat_lon():
    europe_data = pd.read_csv('europe_data.csv')
    route_data = pd.read_csv('europe_route.csv')

    # Merge the merged data with Europe data on Source airport
    merged_data = pd.merge(route_data, europe_data[['IATA', 'Latitude', 'Longitude']], how='left',
                           left_on='Source airport', right_on='IATA')

    # Drop the redundant 'IATA' column
    merged_data.drop(columns=['IATA'], inplace=True)

    # Merge the merged data with Europe data on Destination airport
    merged_data = pd.merge(merged_data, europe_data[['IATA', 'Latitude', 'Longitude']], how='left',
                           left_on='Destination airport', right_on='IATA', suffixes=('_source', '_destination'))

    # Drop the redundant 'IATA' column
    merged_data.drop(columns=['IATA'], inplace=True)
    merged_data.to_csv("europe_route1.csv", index=False)


def haversineformula_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # harversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # radius of earth in kilometers
    return c * r


def update_distance():
    data = pd.read_csv("europe_route1.csv")
    data.columns = ["Airline", "Airline ID", "Source airport", "Source airport ID", "Destination airport",
                    "Destination airport ID", "Codeshare", "Stops", "Equipment", "Source Latitude", "Source Longitude",
                    "Destination Latitude", "Destination Longitude"]
    data['Distance'] = data.apply(lambda row: haversineformula_distance(row['Source Latitude'], row['Source Longitude'], row['Destination Latitude'], row['Destination Longitude']), axis=1)

    data.to_csv("europe_route_distance.csv", index=False)

update_distance()