import pandas as pd


class AirportNode:
    def __init__(self, iata_code, name, city, country, latitude, longitude):
        self.iata_code = iata_code  # IATA code of the airport
        self.name = name  # Name of the airport
        self.city = city  # City where the airport is located
        self.country = country  # Country where the airport is located
        self.latitude = latitude  # Latitude of the airport's location
        self.longitude = longitude  # Longitude of the airport's location


class AirportGraph:
    adjList = {}
    distances = {}

    def __init__(self, file):
        flight_routes = pd.read_csv("europe_flight_dataset.csv")
        for index, row in flight_routes.iterrows():
            source_airport = row['Source Airport IATA']
            destination_airport = row['Destination Airport IATA']
            distance = row['Distance']

            # Add the destination airport to the adjacency list of the source airport
            if source_airport in self.adjList:
                self.adjList[source_airport].append(destination_airport)
            else:
                self.adjList[source_airport] = []
                self.adjList[source_airport].append(destination_airport)

            # Add the source airport to the adjacency list of the destination airport
            if destination_airport in self.adjList:
                self.adjList[destination_airport].append(source_airport)
            else:
                self.adjList[destination_airport] = []
                self.adjList[destination_airport].append(source_airport)

            # Store the distance between the airports
            key = tuple(sorted([source_airport, destination_airport]))
            self.distances[key] = distance

    def get_distance(self, source_airport, destination_airport):
        # Get the distance between two airports
        key = tuple(sorted([source_airport, destination_airport]))
        return self.distances.get(key)

    def adj(self, airport):
        # Return the adjacency list of the given airport
        return self.adjList[airport]


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
    distances = {airport: float('inf') for airport in graph.adjList}
    distances[source_airport] = 0

    # Initialize priority queue with min-heap
    pq = MinHeap()
    pq.insert((0, source_airport))

    while not pq.is_empty():
        current_distance, current_airport = pq.extract_min()

        # If the destination airport is reached, stop
        if current_airport == destination_airport:
            break

        # Visit each neighboring airport of the current airport
        for neighbour in graph.adj(current_airport):
            distance_to_neighbour = current_distance + graph.get_distance(current_airport, neighbour)
            # Update the distance to the neighbor if it's smaller than the recorded distance
            if distance_to_neighbour < distances[neighbour]:
                distances[neighbour] = distance_to_neighbour
                pq.insert((distance_to_neighbour, neighbour))

    # Return the distance to the destination airport
    return distances[destination_airport]


# test
graph = AirportGraph("europe_flight_dataset.csv")
print(find_shortest_path(graph, "CGN", "LHR"))
