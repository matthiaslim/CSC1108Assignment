import pandas as pd
import flight_tracker


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
    merged_data.to_csv("europe_flights_without_distance.csv", index=False)


def calculate_distance():
    data = pd.read_csv("europe_flights_without_distance.csv")
    data.columns = ["Airline", "Airline ID", "Source Airport IATA", "Destination Airport IATA",
                    "Source City", "Source Country", "Destination City", "Destination Country", "Source Latitude",
                    "Source Longitude",
                    "Destination Latitude", "Destination Longitude"]
    data['Distance'] = data.apply(
        lambda row: flight_tracker.haversine_formula_distance(row['Source Latitude'], row['Source Longitude'],
                                                              row['Destination Latitude'],
                                                              row['Destination Longitude']), axis=1)

    data.to_csv("europe_flight_dataset_without_cost.csv", index=False)


def calculate_cost():
    data = pd.read_csv("europe_flight_dataset_without_cost.csv")
    data.columns = ["Airline", "Airline ID", "Source Airport IATA", "Destination Airport IATA",
                    "Source City", "Source Country", "Destination City", "Destination Country", "Source Latitude",
                    "Source Longitude",
                    "Destination Latitude", "Destination Longitude", "Distance"]
    data['Estimated Cost'] = data.apply(
        lambda row: flight_tracker.calculate_flight_cost(row['Distance']), axis=1)

    data.to_csv("europe_flight_dataset.csv", index=False)


def main():
    europe_airports = pd.read_csv('europe_airports.csv')
    europe_routes = pd.read_csv('europe_routes.csv')

    modified_europe_routes = merge_city_country(europe_airports, europe_routes)

    merge_lat_lon(europe_airports, modified_europe_routes)
    calculate_distance()
    calculate_cost()


if __name__ == "__main__":
    main()
