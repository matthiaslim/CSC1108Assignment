import pandas as pd
from math import radians, sin, cos, asin, sqrt, frexp


class AirportNode:
    def __init__(self, iata_code, name, city, country, latitude, longitude):
        self.iata_code = iata_code  # IATA code of the airport
        self.name = name  # Name of the airport
        self.city = city  # City where the airport is located
        self.country = country  # Country where the airport is located
        if latitude in range(-90, 90):
            self.latitude = latitude  # Latitude of the airport's location
        else:
            raise ValueError("Invalid latitude value! (Must be between -90 and 90)")
        if longitude in range(-180, 180):
            self.longitude = longitude  # Longitude of the airport's location
        else:
            raise ValueError("Invalid longitude value! (Must be between -180 and 180")


class RouteEdge:
    def __init__(self, source_airport, destination_airport, distance):
        self.source_airport = source_airport
        self.destination_airport = destination_airport
        self.distance = distance


class AirportGraph:
    airports = {}  # Dictionary to store airports and coordinates
    flights = []  # List to store flight routes and distances

    def __init__(self, airports_file, flights_file):
        try:
            self.load_airports(airports_file)
            self.load_flights(flights_file)

        except FileNotFoundError as e:
            print("File not found: " + str(e))
        except Exception as e:
            print("An error has occurred: " + str(e))

    def load_airports(self, airports_file):
        airports_df = pd.read_csv(airports_file)

        for index, row in airports_df.iterrows():
            self.add_airport(row['IATA'], row['Latitude'], row['Longitude'])

    def load_flights(self, flights_file):
        flights_df = pd.read_csv(flights_file)

        for index, row in flights_df.iterrows():
            self.add_flight(row['Source Airport IATA'], row['Destination Airport IATA'], row['Distance'])

    def add_airport(self, code, lat, lon):
        self.airports[code] = (lat, lon)

    def add_flight(self, source_airport, destination_airport, distance):
        self.flights.append((source_airport, destination_airport, distance))

    def get_neighbors(self, airport):
        # Get neighboring airports for a given airport
        return [flight[1] for flight in self.flights if flight[0] == airport]

    def get_distance(self, source_airport, destination_airport):
        # Get the distance between two airports
        for flight in self.flights:
            if flight[0] == source_airport and flight[1] == destination_airport:
                return flight[2]  # Return distance between the two airports
        return None  # Return None is distance is not found

    # Calculate distance between two airports without a direct flight
    def calculate_distance(self, source_airport, destination_airport):
        flight_distance = self.get_distance(source_airport, destination_airport)
        if flight_distance is not None:
            return flight_distance
        else:
            return haversine_formula_distance(self.airports[source_airport][0],
                                              self.airports[source_airport][1],
                                              self.airports[destination_airport][0],
                                              self.airports[destination_airport][1])


# Creating fibonacci tree
class FibonacciTree:
    def __init__(self, value):
        self.value = value
        self.child = []
        self.order = 0

    # Adding tree at the end of the tree
    def add_at_end(self, t):
        self.child.append(t)
        self.order = self.order + 1


# Creating Fibonacci heap
class FibonacciHeap:
    def __init__(self):
        self.trees = []
        self.least = None
        self.count = 0

    # Insert a node
    def insert_node(self, value):
        new_tree = FibonacciTree(value)
        self.trees.append(new_tree)
        if self.least is None or value < self.least.value:
            self.least = new_tree
        self.count = self.count + 1

    # Get minimum value
    def get_min(self):
        if self.least is None:
            return None
        return self.least.value

    # Extract the minimum value
    def extract_min(self):
        smallest = self.least
        if smallest is not None:
            for child in smallest.child:
                self.trees.append(child)
            self.trees.remove(smallest)
            if not self.trees:
                self.least = None
            else:
                self.least = self.trees[0]
                self.consolidate()
            self.count = self.count - 1
            return smallest.value

    # Consolidate the tree
    def consolidate(self):
        aux = (floor_log(self.count) + 1) * [None]

        while self.trees:
            x = self.trees[0]
            order = x.order
            self.trees.remove(x)
            while aux[order] is not None:
                y = aux[order]
                if x.value > y.value:
                    x, y = y, x
                x.add_at_end(y)
                aux[order] = None
                order = order + 1
            aux[order] = x

        self.least = None
        for k in aux:
            if k is not None:
                self.trees.append(k)
                if (self.least is None
                        or k.value < self.least.value):
                    self.least = k


def floor_log(x):
    return frexp(x)[1] - 1


def haversine_formula_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # radius of earth in kilometers
    return c * r


def group_airports_by_country(airports_df):
    airports_by_country = airports_df.groupby('Country')['Name_IATA'].apply(list).to_dict()
    return airports_by_country


def airports_data():
    europe_airports = pd.read_csv("europe_airports.csv")
    europe_airports['Name_IATA'] = europe_airports['Name'] + ' (' + europe_airports['IATA'] + ')'

    airports_by_country = group_airports_by_country(europe_airports)
    # print(airports_by_country)
    return airports_by_country


def read_airports_from_csv():
    airports = []
    df = pd.read_csv("europe_airports.csv")
    for _, row in df.iterrows():
        airport = AirportNode(row['IATA'], row['Name'], row['City'], row['Country'], row['Latitude'], row['Longitude'])
        airports.append(airport)
    print(airports)
    return airports


# find the shortest path between two airports using Dijkstra's shortest path algorithm
def find_shortest_path(graph, source_airport, destination_airport):
    # Initialize distances to all airports as infinity
    distances = {airport: float('inf') for airport in graph.airports}
    distances[source_airport] = 0

    # Initialize a dictionary to store the previous airport for each airport
    previous_airport = {}

    # Initialise priority queue with fibonacci heap
    f_heap = FibonacciHeap()
    f_heap.insert_node((0, source_airport))

    while f_heap.count > 0:
        current_distance, current_airport = f_heap.extract_min()

        # If the destination airport is reached, stop
        if current_airport == destination_airport:
            break

        # Visit each neighboring airport of the current airport
        for neighbour in graph.get_neighbors(current_airport):
            distance_to_neighbour = current_distance + graph.calculate_distance(current_airport, neighbour)
            # Update the distance to the neighbor if it's smaller than the recorded distance
            if distance_to_neighbour < distances[neighbour]:
                distances[neighbour] = distance_to_neighbour
                #  Update the path taken
                previous_airport[neighbour] = current_airport
                f_heap.insert_node((distance_to_neighbour, neighbour))

    # Initialise an array to store shortest path taken to reach destination
    shortest_path = []
    current_airport = destination_airport
    # Reconstruct the shortest path using the previous airport dictionary
    while current_airport != source_airport:
        shortest_path.append(current_airport)
        current_airport = previous_airport[current_airport]
    shortest_path.append(source_airport)

    # Return the shortest path to the destination airport
    return shortest_path[::-1]


# test
graph = AirportGraph("europe_airports.csv", "europe_flight_dataset.csv")
print(find_shortest_path(graph, "NTE", "LHR"))
