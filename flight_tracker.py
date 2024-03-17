import pandas as pd
import os


class AirportNode:
    def __init__(self, iata_code, name, city, country, latitude, longitude):
        self.iata_code = iata_code  # IATA code of the airport
        self.name = name  # Name of the airport
        self.city = city  # City where the airport is located
        self.country = country  # Country where the airport is located
        if latitude in range(-90, 90):
            self.latitude = latitude  # Latitude of the airport's location
        else:
            print("Invalid latitude value! (Must be between -90 and 90)")
            return
        if longitude in range(-180, 180):
            self.longitude = longitude  # Longitude of the airport's location
        else:
            print("Invalid longitude value! (Must be between -180 and 180")
            return


class AirportGraph:
    adjList = {}
    distances = {}

    def __init__(self, file):
        try:
            flight_routes = pd.read_csv(file)
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
        except FileNotFoundError:
            print("File not found: " + file)
        except Exception as e:
            print("An error has occurred: " + str(e))

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

    # Initialize a dictionary to store the previous airport for each airport
    previous_airport = {}

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
                #  Update the path taken
                previous_airport[neighbour] = current_airport
                pq.decrease_key(distance_to_neighbour, neighbour)

    # Initialise an array to store shortest path taken to reach destination
    shortest_path = []
    current_airport = destination_airport
    # Reconstruct the shortest path using the previous airport dictionary
    while current_airport != source_airport:
        shortest_path.append(current_airport)
        current_airport = previous_airport[current_airport]
    shortest_path.append(source_airport)

    # Return the shortest path to the destination airport
    return shortest_path


# test
graph = AirportGraph("europe_flight_dataset.csv")
print(find_shortest_path(graph, "CGN", "LHR"))
