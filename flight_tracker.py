import pandas as pd
import heapq
from math import radians, sin, cos, asin, sqrt


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


class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    # insert a new key into the heap
    def insert(self, key):
        self.heap.append(key)
        i = len(self.heap) - 1
        while i > 0 and self.heap[self.parent(i)] > self.heap[i]:
            self.heap[self.parent(i)], self.heap[i] = self.heap[i], self.heap[self.parent(i)]
            i = self.parent(i)

    # Remove and return minimum key from heap
    def extract_min(self):
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.min_heapify(0)
        return root

    # Ensure that the subtree at index i satisfies the minimum heap property
    def min_heapify(self, i):
        left_child = 2 * i + 1
        right_child = 2 * i + 2
        smallest = i
        if left_child < len(self.heap) and self.heap[left_child] < self.heap[i]:
            smallest = left_child
        if right_child < len(self.heap) and self.heap[right_child] < self.heap[smallest]:
            smallest = right_child
        if smallest != i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self.min_heapify(smallest)

    # Return the minimum key in the heap
    def get_min(self):
        if len(self.heap) > 0:
            return self.heap[0]
        return None

    # check if the heap is empty
    def is_empty(self):
        return len(self.heap) == 0

    def decrease_key(self, vertex, new_distance):
        # Find the index of the vertex in the heap
        index = None
        for i, (distance, v) in enumerate(self.heap):
            if v == vertex:
                index = i
                break

        # If the vertex is not found, do nothing
        if index is None:
            return

        # Update the distance of the vertex and adjust the heap if necessary
        if new_distance < self.heap[index][0]:
            self.heap[index] = (new_distance, vertex)
            while index > 0 and self.heap[self.parent(index)][0] > self.heap[index][0]:
                self.heap[self.parent(index)], self.heap[index] = self.heap[index], self.heap[self.parent(index)]
                index = self.parent(index)


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

    # Initialize priority queue with min-heap
    # priority_q = MinHeap()
    # priority_q.insert((0, source_airport))

    # Initialise priority queue with heapq
    priority_q = [(0, source_airport)]

    while priority_q:
        # current_distance, current_airport = priority_q.extract_min()
        current_distance, current_airport = heapq.heappop(priority_q)

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
                # priority_q.decrease_key(distance_to_neighbour, neighbour)
                heapq.heappush(priority_q, (distance_to_neighbour, neighbour))

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
