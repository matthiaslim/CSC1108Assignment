from collections import deque
import pandas as pd
from math import radians, sin, cos, asin, sqrt, frexp


class AirportNode:
    def __init__(self, iata_code, name, city, country, latitude, longitude):
        self.iata_code = iata_code  # IATA code of the airport
        self.name = name  # Name of the airport
        self.city = city  # City where the airport is located
        self.country = country  # Country where the airport is located
        self.latitude = latitude  # Latitude of the airport's location
        self.longitude = longitude  # Longitude of the airport's location
        self.routes = []  # list to store all available routes

    def add_route_edge(self, destination_airport, distance):
        route_edge = RouteEdge(self.iata_code, destination_airport, distance)
        self.routes.append(route_edge)


class RouteEdge:
    def __init__(self, source_airport, destination_airport, distance):
        self.source_airport = source_airport
        self.destination_airport = destination_airport
        self.distance = distance


class FlightGraph:
    airports = {}  # Adjacency list to store airports as nodes flight routes as edges

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
            airport = AirportNode(row['IATA'], row['Name'], row['City'], row['Country'], row['Latitude'],
                                  row['Longitude'])
            self.add_airport(row['IATA'], airport)

    def load_flights(self, flights_file):
        flights_df = pd.read_csv(flights_file)

        for index, row in flights_df.iterrows():
            self.add_flight_route(row['Source Airport IATA'], row['Destination Airport IATA'], row['Distance'])

    def add_airport(self, code, airport):
        self.airports[code] = airport

    def add_flight_route(self, source_airport, destination_airport, distance):
        if source_airport in self.airports and destination_airport in self.airports:
            source_node = self.airports[source_airport]
            source_node.add_route_edge(destination_airport, distance)

    def get_routes(self, airport):
        return self.airports[airport].routes

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
                return route.distance

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

    def group_airports_by_country(self):
        data = []
        for iata, airport in self.airports.items():
            data.append(
                {'IATA': airport.iata_code, 'Name': airport.name, 'City': airport.city, 'Country': airport.country})
        airports_df = pd.DataFrame(data)
        airports_df['Name_IATA'] = airports_df['Name'] + ' (' + airports_df['IATA'] + ')'
        airports_by_country = airports_df.groupby('Country')['Name_IATA'].apply(list).to_dict()
        return airports_by_country

    # find the shortest path between two airports using Dijkstra's shortest path algorithm
    def find_shortest_path(self, source_airport, destination_airport):
        # Check if flight data from source airport exist in the graph
        if not self.get_routes(source_airport):
            print(f"Flights from '{source_airport}' do not exist.")
            return None

        # Clear shortest path memory
        distances = {}
        previous_airport = {}  # Initialize a dictionary to store the previous airport for each airport

        # Initialize distances to all airports as infinity
        distances = {airport: float('inf') for airport in self.airports}
        distances[source_airport] = 0

        # Initialise priority queue with fibonacci heap
        f_heap = FibonacciHeap()
        f_heap.insert_node((0, source_airport))

        while f_heap.count > 0:
            current_distance, current_airport = f_heap.extract_min()

            # If the destination airport is reached, stop
            if current_airport == destination_airport:
                break

            # Visit each neighboring airport of the current airport
            for neighbour in self.get_neighbors(current_airport):
                distance_to_neighbour = current_distance + self.calculate_distance(current_airport, neighbour)
                # Update the distance to the neighbor if it's smaller than the recorded distance
                if distance_to_neighbour < distances[neighbour]:
                    distances[neighbour] = distance_to_neighbour
                    #  Update the path taken
                    previous_airport[neighbour] = current_airport
                    f_heap.insert_node((distance_to_neighbour, neighbour))

        # Check if there are direct flights from the source to the destination airport
        if distances[destination_airport] == float('inf'):
            print(f"No direct flights from {source_airport} to {destination_airport}.")
            # Find the nearest airport to the destination recursively
            nearest_airport = self.find_nearest_airport(destination_airport)
            print(f"Rerouting to nearest airport {nearest_airport}.")
            destination_airport = nearest_airport

            # Restart the search from the source airport to the nearest airport
            return self.find_shortest_path(source_airport, destination_airport)

        # Initialise a list to store shortest path taken to reach destination
        shortest_path = []
        current_airport = destination_airport
        # Reconstruct the shortest path using the previous airport dictionary
        while current_airport != source_airport:
            shortest_path.append(current_airport)
            current_airport = previous_airport[current_airport]
        shortest_path.append(source_airport)

        if len(shortest_path) < 2:
            # If the list only contains source airport, return None
            return None
        else:
            # Else, return the shortest path to the destination airport
            return shortest_path[::-1]

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

    # Function to perform Breadth First Search on the flight graph to return path with the least route edges
    def least_layovers_bfs(self, source_airport, destination_airport):
        # Create a queue for BFS
        queue = deque()
        visited = set()

        # Initialize a dictionary to track the path and the number of layovers
        path_with_layovers = {source_airport: (None, 0)}  # (Previous airport, layover count)

        # Mark the source airport as visited and enqueue it along with the initial layover count of 0
        queue.append(source_airport)
        visited.add(source_airport)

        # Iterate over the queue
        while queue:
            # Dequeue a vertex from the queue
            current_airport = queue.popleft()

            # Check if the current airport is the destination
            if current_airport == destination_airport:
                # Reconstruct the path from the destination to the source
                path = []
                layovers = path_with_layovers[current_airport][1]
                while current_airport:
                    path.append(current_airport)
                    current_airport = path_with_layovers[current_airport][0]
                path.reverse()
                return path, layovers  # Return the path and the number of layovers

            # Get all adjacent airports (neighbors) of the current airport
            adjacent_airports = [route.destination_airport for route in self.airports[current_airport].routes]

            # Enqueue neighboring airports that have not been visited
            for neighbor in adjacent_airports:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    # Increment the layover count only if the neighbor is not the destination airport
                    layover_count = path_with_layovers[current_airport][1]
                    if neighbor != destination_airport:
                        layover_count += 1
                    path_with_layovers[neighbor] = (current_airport, layover_count)

        # If destination airport is not reachable
        return None, -1  # or any appropriate indicator


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


# test
graph = FlightGraph("europe_airports.csv", "europe_flight_dataset.csv")
print(graph.least_layovers_bfs("LHR", "CRA"))
