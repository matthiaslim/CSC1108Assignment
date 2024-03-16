import pandas as pd


class AirportNode:
    def __init__(self, iata_code, name, city, country, latitude, longitude):
        self.iata_code = iata_code  # IATA code of the airport
        self.name = name            # Name of the airport
        self.city = city            # City where the airport is located
        self.country = country      # Country where the airport is located
        self.latitude = latitude    # Latitude of the airport's location
        self.longitude = longitude  # Longitude of the airport's location


def group_airports_by_country(airports_df):
    airports_by_country = airports_df.groupby('Country')['Name_IATA'].apply(list).to_dict()
    return airports_by_country


def airports_data():
    europe_airports = pd.read_csv("europe_airports.csv")
    europe_airports['Name_IATA'] = europe_airports['Name'] + ' (' + europe_airports['IATA'] + ')'

    airports_by_country = group_airports_by_country(europe_airports)
    #print(airports_by_country)
    return airports_by_country

def read_airports_from_csv():
    airports = []
    df = pd.read_csv("europe_airports.csv")
    for _, row in df.iterrows():
        airport = AirportNode(row['IATA'], row['Name'], row['City'], row['Country'], row['Latitude'], row['Longitude'])
        airports.append(airport)
    print(airports)
    return airports

