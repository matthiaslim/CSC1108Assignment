import os
import pandas as pd
from utils.calculation_utils import haversine_formula_distance
from models.airport import AirportNode
from algorithms.flight_path_algorithms import Dijkstra, BFS, AStar


class FlightGraph:
    airports = {}  # Adjacency list to store airports as nodes flight routes as edges

    def __init__(self, airports_file, flights_file):
        try:
            if not os.path.isfile(airports_file):
                raise FileNotFoundError(f"Airports file '{airports_file}' not found.")
            if not os.path.isfile(flights_file):
                raise FileNotFoundError(f"Flights file '{flights_file}' not found.")

            self.load_airports(airports_file)
            self.load_flights(flights_file)
        except FileNotFoundError as e:
            print("File not found: " + str(e))
        except Exception as e:
            print("An error has occurred: " + str(e))
        finally:
            self.dijkstra = Dijkstra(self)
            self.bfs = BFS(self)
            self.astar = AStar(self)

    def load_airports(self, airports_file):
        airports_df = pd.read_csv(airports_file)

        for index, row in airports_df.iterrows():
            airport = AirportNode(row['IATA'], row['Name'], row['City'], row['Country'], row['Latitude'],
                                  row['Longitude'])
            self.add_airport(row['IATA'], airport)

    def load_flights(self, flights_file):
        flights_df = pd.read_csv(flights_file)

        for index, row in flights_df.iterrows():
            self.add_flight_route(row['Source Airport IATA'], row['Destination Airport IATA'], row['Distance'],
                                  row['Estimated Cost'], row['Estimated Duration'])

    def add_airport(self, code, airport):
        self.airports[code] = airport

    def add_flight_route(self, source_airport, destination_airport, distance, cost, duration):
        if source_airport in self.airports and destination_airport in self.airports:
            source_node = self.airports[source_airport]
            weights = {'distance': distance, 'cost': cost, 'duration': duration}
            source_node.add_route_edge(destination_airport, weights)

    def get_routes(self, airport):
        return self.airports[airport].routes

    def get_routes_to(self, destination_airport):
        routes_to_airport = []
        for airport in self.airports:
            for airport_route in self.airports[airport].routes:
                if airport_route.destination_airport == destination_airport:
                    routes_to_airport.append(airport_route)
        return routes_to_airport

    def get_neighbors(self, airport):
        # Get neighboring airports for a given airport
        if airport in self.airports:
            return [route.destination_airport for route in self.airports[airport].routes]
        else:
            return []

    def get_distance(self, source_airport, destination_airport):
        # Check if source and destination airports are valid
        if source_airport not in self.airports or destination_airport not in self.airports:
            return None

        # Get routes for the source airport
        source_routes = self.airports[source_airport].routes

        # Iterate over routes to find a matching destination airport
        for route in source_routes:
            if route.destination_airport == destination_airport:
                return route.get_weight('distance')

        # If no matching route is found, return None
        return None

    # Calculate distance between two airports without a direct flight
    def calculate_distance(self, source_airport, destination_airport):
        flight_distance = self.get_distance(source_airport, destination_airport)
        if flight_distance is not None:
            return flight_distance
        else:
            return haversine_formula_distance(self.airports[source_airport].latitude,
                                              self.airports[source_airport].longitude,
                                              self.airports[destination_airport].latitude,
                                              self.airports[destination_airport].longitude)

    def get_flight_cost(self, source_airport, destination_airport):
        # Check if source and destination airports are valid
        if source_airport not in self.airports or destination_airport not in self.airports:
            return float('inf')

        # Get routes for the source airport
        source_routes = self.airports[source_airport].routes

        # Iterate over routes to find a matching destination airport
        for route in source_routes:
            if route.destination_airport == destination_airport:
                return route.get_weight('cost')

        # If no matching route is found, return infinite
        return float('inf')

    def get_flight_duration(self, source_airport, destination_airport):
        # Check if source and destination airports are valid
        if source_airport not in self.airports or destination_airport not in self.airports:
            return float('inf')

        # Get routes for the source airport
        source_routes = self.airports[source_airport].routes

        # Iterate over routes to find a matching destination airport
        for route in source_routes:
            if route.destination_airport == destination_airport:
                return route.get_weight('duration')

        # If no matching route is found, return infinite
        return float('inf')

    def group_airports_by_country(self):
        data = []
        for iata, airport in self.airports.items():
            data.append(
                {'IATA': airport.iata_code, 'Name': airport.name, 'City': airport.city, 'Country': airport.country})
        airports_df = pd.DataFrame(data)
        airports_df['Name_IATA'] = airports_df['Name'] + ' (' + airports_df['IATA'] + ')'
        airports_by_country = airports_df.groupby('Country')['Name_IATA'].apply(list).to_dict()
        return airports_by_country

    def get_route_information(self, route_path):
        if not route_path or len(route_path) < 2:
            return {"error": "Invalid route path. It must contain at least two airports."}

        # Calculate total stops, distance, cost, and duration
        stops = len(route_path) - 2
        cost = 0
        duration = 0
        distance = 0
        for i in range(len(route_path) - 1):
            current_airport = route_path[i]
            next_airport = route_path[i + 1]
            distance += self.calculate_distance(current_airport, next_airport)
            cost += self.get_flight_cost(current_airport, next_airport)
            duration += self.get_flight_duration(current_airport, next_airport)
            # Add 2 hours for layover duration
            if i < len(route_path) - 2:
                duration += 2

        # Return the result
        return {"path": route_path,
                "distance": distance,
                "stops": stops,
                "cost": cost,
                "duration": duration}

    def find_nearest_airport(self, destination_airport):
        # Find the nearest airport to the destination
        nearest_distance = float('inf')
        nearest_airport = None

        for airport in self.airports:
            if airport != destination_airport:
                distance = self.calculate_distance(airport, destination_airport)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_airport = airport

        return nearest_airport

    def find_route(self, source_airport, destination_airport, criteria, intermediate_airports=None):
        try:
            if source_airport not in self.airports:
                raise ValueError(f"Invalid source airport: '{source_airport}'")
            if destination_airport not in self.airports:
                raise ValueError(f"Invalid destination airport: '{destination_airport}'")
            if criteria not in ["optimal", "shortest distance", "least cost", "shortest duration", "least layovers"]:
                raise ValueError("Invalid criteria selected.")

            if intermediate_airports is None:
                intermediate_airports = []

            # Check if multi-city flight is required based on the given criteria
            if criteria in ["optimal", "shortest distance", "least cost", "shortest duration", "least layovers"] \
                    and intermediate_airports:
                # Handle multi-city flights
                if criteria == "shortest distance":
                    return self.dijkstra.find_shortest_distance_multi(source_airport,
                                                                      destination_airport, intermediate_airports)
                # elif criteria == "least cost":
                #     return self.dijkstra.find_least_cost_multi(source_airport, destination_airport, intermediate_airports)
                # elif criteria == "shortest duration":
                #     return self.dijkstra.find_shortest_duration_multi(source_airport, destination_airport, intermediate_airports)
                # elif criteria == "least layovers":
                #     return self.bfs.find_least_layovers_multi(source_airport, destination_airport, intermediate_airports)
            else:
                # Handle single-city flights
                if criteria == "optimal":
                    return self.astar.find_optimal_flight(source_airport, destination_airport)
                elif criteria == "shortest distance":
                    return self.dijkstra.find_shortest_distance(source_airport, destination_airport)
                elif criteria == "least cost":
                    return self.dijkstra.find_least_cost(source_airport, destination_airport)
                elif criteria == "shortest duration":
                    return self.dijkstra.find_shortest_duration(source_airport, destination_airport)
                elif criteria == "least layovers":
                    return self.bfs.find_least_layovers(source_airport, destination_airport)
        except ValueError as e:
            print("Input Validation error:", e)
            return None


# test
graph = FlightGraph("data/europe_airports.csv", "data/europe_flight_dataset.csv")
print(graph.find_route("BOJ", "UHE", "shortest distance"))
print(graph.find_route("LHR", "SUF", "shortest distance", ['AMS', 'ZRH']))
