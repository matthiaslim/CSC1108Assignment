import pandas as pd


def merge_city_country(airports_df, routes_df):
    city_country_data = airports_df[['IATA', 'City', 'Country']]
    merged_data = pd.merge(routes_df, city_country_data, how='left', left_on='Source airport', right_on='IATA')

    merged_data.drop(columns=['IATA'], inplace=True)

    merged_data = pd.merge(merged_data, city_country_data, how='left',
                           left_on='Destination airport', right_on='IATA', suffixes=('_source', '_destination'))

    merged_data.drop(columns=['IATA'], inplace=True)
    return merged_data


def merge_lat_lon(airports_df, routes_df):
    # Merge the merged data with Europe data on Source airport
    merged_data = pd.merge(routes_df, airports_df[['IATA', 'Latitude', 'Longitude']], how='left',
                           left_on='Source airport', right_on='IATA')

    # Drop the redundant 'IATA' column
    merged_data.drop(columns=['IATA'], inplace=True)

    # Merge the merged data with Europe data on Destination airport
    merged_data = pd.merge(merged_data, airports_df[['IATA', 'Latitude', 'Longitude']], how='left',
                           left_on='Destination airport', right_on='IATA', suffixes=('_source', '_destination'))

    # Drop the redundant 'IATA' column
    merged_data.drop(columns=['IATA'], inplace=True)
    merged_data.to_csv("../data/europe_flights_without_distance.csv", index=False)