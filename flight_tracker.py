import heapq
from collections import deque
import pandas as pd
from math import radians, sin, cos, asin, sqrt, ceil


class AirportNode:
    def __init__(self, iata_code, name, city, country, latitude, longitude):
        self.iata_code = iata_code  # IATA code of the airport
        self.name = name  # Name of the airport
        self.city = city  # City where the airport is located
        self.country = country  # Country where the airport is located
        self.latitude = latitude  # Latitude of the airport's location
        self.longitude = longitude  # Longitude of the airport's location
        self.routes = []  # list to store all available routes

    def add_route_edge(self, destination_airport, weights):
        route_edge = RouteEdge(self.iata_code, destination_airport, weights)
        self.routes.append(route_edge)


class RouteEdge:
    def __init__(self, source_airport, destination_airport, weights):
        self.source_airport = source_airport
        self.destination_airport = destination_airport
        self.weights = weights  # Dictionary to store weights

    def get_weight(self, weight_name):
        return self.weights.get(weight_name)


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
            self.add_flight_route(row['Source Airport IATA'], row['Destination Airport IATA'], row['Distance'],
                                  row['Estimated Cost'])

    def add_airport(self, code, airport):
        self.airports[code] = airport

    def add_flight_route(self, source_airport, destination_airport, distance, cost):
        if source_airport in self.airports and destination_airport in self.airports:
            source_node = self.airports[source_airport]
            weights = {'distance': distance, 'cost': cost}
            source_node.add_route_edge(destination_airport, weights)

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
            return None

        # Get routes for the source airport
        source_routes = self.airports[source_airport].routes

        # Iterate over routes to find a matching destination airport
        for route in source_routes:
            if route.destination_airport == destination_airport:
                return route.get_weight('cost')

        # If no matching route is found, return None
        return None

    def group_airports_by_country(self):
        data = []
        for iata, airport in self.airports.items():
            data.append(
                {'IATA': airport.iata_code, 'Name': airport.name, 'City': airport.city, 'Country': airport.country})
        airports_df = pd.DataFrame(data)
        airports_df['Name_IATA'] = airports_df['Name'] + ' (' + airports_df['IATA'] + ')'
        airports_by_country = airports_df.groupby('Country')['Name_IATA'].apply(list).to_dict()
        return airports_by_country

    def match_iata(self):
        data = []
        for iata,airport in self.airports.items():
            data.append({'Name': airport.name,'IATA': airport.iata_code})
        return data

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

        # Initialize priority queue with a simple list
        priority_queue = [(0, source_airport)]

        while priority_queue:
            current_distance, current_airport = heapq.heappop(priority_queue)

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
                    heapq.heappush(priority_queue, (distance_to_neighbour, neighbour))

        # Check if there are flights (direct/with stop) from the source to the destination airport
        if distances[destination_airport] == float('inf'):
            print(f"No flights from {source_airport} to {destination_airport}.")
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

    def cheapest_flight_astar(self, source_airport, destination_airport):
        # Check if flight data from source airport exist in the graph
        if not self.get_routes(source_airport):
            print(f"Flights from '{source_airport}' do not exist.")
            return None

        # Initialize a dictionary to store the previous airport for each airport
        previous_airport = {}

        # Dict to store the actual cost from source to each node
        g_score = {iata: float('inf') for iata in self.airports}
        g_score[source_airport] = 0

        # Initialize priority queue with a simple list
        priority_queue = [(0, source_airport)]

        while priority_queue:
            current_cost, current_airport = heapq.heappop(priority_queue)

            # If the destination airport is reached, stop
            if current_airport == destination_airport:
                break

            # Visit each neighboring airport of the current airport
            for neighbour in self.get_neighbors(current_airport):
                tentative_g_score = current_cost + self.calculate_distance(current_airport, neighbour)
                # Update the distance to the neighbor if it's smaller than the recorded distance
                if tentative_g_score < g_score[neighbour]:
                    g_score[neighbour] = tentative_g_score
                    # Calculate the estimated total cost from the source to the destination through the neighbor
                    # (using the heuristic, which is the estimated flight cost in this case)
                    h_score = self.get_flight_cost(current_airport, neighbour)
                    f_score = tentative_g_score + h_score
                    # Update the path taken
                    previous_airport[neighbour] = current_airport
                    heapq.heappush(priority_queue, (f_score, neighbour))

        # check if destination reachable
        if destination_airport not in previous_airport:
            print(f"No route found from {source_airport} to {destination_airport}.")
            return None

        # Reconstruct the shortest path from the previous_airport dictionary
        shortest_path = []
        flight_cost = 0  # Variable to store total flight cost
        current_airport = destination_airport
        while current_airport != source_airport:
            shortest_path.append(current_airport)
            flight_cost += self.get_flight_cost(previous_airport[current_airport], current_airport)
            current_airport = previous_airport[current_airport]
        shortest_path.append(source_airport)
        if len(shortest_path) < 2:
            # If the list only contains source airport, return None
            return None
        else:
            # Else, return the shortest path to the destination airport
            return shortest_path[::-1], flight_cost


def haversine_formula_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # radius of earth in kilometers
    return c * r


# function to calculate flight cost based on the distance in kilometres
def calculate_flight_cost(distance):
    base_cost = 25  # set the base cost of flights to be $25
    cost_per_km = 0  # initialise a cost per kilometre that would change based on the distance travelled

    if distance < 600:
        # Shortest flights (under 600km)
        cost_per_km = 0.19
    elif distance < 1000:
        # Short haul (600km to under 1000km)
        cost_per_km = 0.2
    elif distance < 1500:
        # Medium haul (1000km to under 1500km)
        cost_per_km = 0.22
    else:
        # Long-haul (1500km and above)
        cost_per_km = 0.25

    # calculate the total cost of the flight as base cost with the added total cost per km
    total_cost = base_cost + (distance * cost_per_km)
    return ceil(total_cost)  # return the total cost rounded up to the nearest whole number


# test
graph = FlightGraph("europe_airports.csv", "europe_flight_dataset.csv")
print(graph.least_layovers_bfs("DBV", "KDL"))
print(graph.find_shortest_path("DBV", "KDL"))
print(graph.cheapest_flight_astar("DBV", "KDL"))
#print(graph.match_iata())
#print(graph.group_airports_by_country())