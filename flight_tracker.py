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


def main():
    europe_airports = pd.read_csv("europe_airports.csv")
    europe_airports['Name_IATA'] = europe_airports['Name'] + ' (' + europe_airports['IATA'] + ')'

    airports_by_country = group_airports_by_country(europe_airports)
    print(airports_by_country)


if __name__ == "__main__":
    main()
