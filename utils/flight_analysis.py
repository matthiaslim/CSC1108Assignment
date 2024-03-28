import pandas as pd
from utils.calculation_utils import haversine_formula_distance, calculate_flight_cost, calculate_flight_duration


def calculate_distance():
    data = pd.read_csv("../data/europe_flights_without_distance.csv")
    data.columns = ["Airline", "Airline ID", "Source Airport IATA", "Destination Airport IATA",
                    "Source City", "Source Country", "Destination City", "Destination Country", "Source Latitude",
                    "Source Longitude",
                    "Destination Latitude", "Destination Longitude"]
    data['Distance'] = data.apply(
        lambda row: haversine_formula_distance(row['Source Latitude'], row['Source Longitude'],
                                               row['Destination Latitude'],
                                               row['Destination Longitude']), axis=1)

    data.to_csv("../data/europe_flight_dataset_without_cost.csv", index=False)


def calculate_cost():
    data = pd.read_csv("../data/europe_flight_dataset_without_cost.csv")
    data.columns = ["Airline", "Airline ID", "Source Airport IATA", "Destination Airport IATA",
                    "Source City", "Source Country", "Destination City", "Destination Country", "Source Latitude",
                    "Source Longitude",
                    "Destination Latitude", "Destination Longitude", "Distance"]
    data['Estimated Cost'] = data.apply(
        lambda row: calculate_flight_cost(row['Distance']), axis=1)

    data.to_csv("../data/europe_flight_dataset_without_duration.csv", index=False)


def calculate_duration():
    data = pd.read_csv("../data/europe_flight_dataset_without_duration.csv")
    data.columns = ["Airline", "Airline ID", "Source Airport IATA", "Destination Airport IATA",
                    "Source City", "Source Country", "Destination City", "Destination Country", "Source Latitude",
                    "Source Longitude",
                    "Destination Latitude", "Destination Longitude", "Distance", "Estimated Cost"]
    data['Estimated Duration'] = data.apply(
        lambda row: calculate_flight_duration(row['Distance']), axis=1)

    data.to_csv("../data/europe_flight_dataset.csv", index=False)
