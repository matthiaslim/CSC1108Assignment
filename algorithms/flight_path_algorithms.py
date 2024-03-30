import heapq
from collections import deque


class Dijkstra:
    def __init__(self, graph):
        """
        Initialize Dijkstra's algorithm with the given graph.

        Args:
            graph (Graph): The graph representing flight routes.
        """
        self.graph = graph

    # find the shortest distance path between two airports using Dijkstra's shortest path algorithm
    def find_shortest_distance(self, source_airport, destination_airport):
        """
            Find the shortest distance path between two airports using Dijkstra's shortest path algorithm.

            Args:
                source_airport (str): The IATA code of the source airport.
                destination_airport (str): The IATA code of the destination airport.

            Returns:
                dict or None: A dictionary containing information about the shortest distance route,
                              including the flight path, segments, total stops, total cost, total duration,
                              and total layover time. Returns None if no valid route is found.
        """
        # Check if flight data from source airport exist in the graph
        if not self.graph.get_routes(source_airport):
            print(f"Flights from '{source_airport}' do not exist.")
            return None

        # Check if flight data to destination airport exist in the graph
        if not self.graph.get_routes_to(destination_airport):
            print(f"Flights to '{destination_airport}' do not exist")
            # Find the nearest airport to the destination recursively
            nearest_airport = self.graph.find_nearest_airport(destination_airport)
            print(f"Rerouting to nearest airport {nearest_airport}.")

            # Check if the nearest airports has routes to it
            if nearest_airport is None or not self.graph.get_routes_to(nearest_airport):
                print(f"No flights to {nearest_airport}.")
                return None

            destination_airport = nearest_airport

            # Restart the search from the source airport to the nearest airport
            return self.find_shortest_distance(source_airport, destination_airport)

        # Clear shortest path memory
        distances = {}
        previous_airport = {}  # Initialize a dictionary to store the previous airport for each airport

        # Initialize distances to all airports as infinity
        distances = {airport: float('inf') for airport in self.graph.airports}
        distances[source_airport] = 0

        # Initialize priority queue with a simple list
        priority_queue = [(0, source_airport)]

        while priority_queue:
            current_distance, current_airport = heapq.heappop(priority_queue)

            # If the destination airport is reached, stop
            if current_airport == destination_airport:
                break

            # Visit each neighboring airport of the current airport
            for neighbour in self.graph.get_neighbors(current_airport):
                distance_to_neighbour = current_distance + self.graph.calculate_distance(current_airport, neighbour)
                # Update the distance to the neighbor if it's smaller than the recorded distance
                if distance_to_neighbour < distances[neighbour]:
                    distances[neighbour] = distance_to_neighbour
                    #  Update the path taken
                    previous_airport[neighbour] = current_airport
                    heapq.heappush(priority_queue, (distance_to_neighbour, neighbour))

        # Reconstruct the shortest path from the previous_airport dictionary
        shortest_path = []
        current_airport = destination_airport
        while current_airport != source_airport:
            shortest_path.append(current_airport)
            current_airport = previous_airport[current_airport]
        shortest_path.append(source_airport)

        # Reverse the path to get it in the correct order
        shortest_path.reverse()

        # Get route information
        route = self.graph.get_route_information(shortest_path)

        # Return the route information
        return route

    def find_shortest_distance_multi(self, source_airport, destination_airport, intermediate_airports):
        """
            Find the shortest distance multi-flight route between two airports with intermediate stops.

            Args:
                source_airport (str): The IATA code of the source airport.
                destination_airport (str): The IATA code of the destination airport.
                intermediate_airports (list of str): List of IATA codes of intermediate airports.

            Returns:
                dict or None: A dictionary containing information about the shortest distance multi-flight route,
                              including the flight path, segments, total stops, total cost, total duration,
                              and total layover time. Returns None if no valid route is found.
        """
        # Initialize variables
        multi_flight_segments = []
        current_source = source_airport
        flight_path = [current_source]
        total_layover_time = 0

        # Find the shortest distance for each segment of the multi-flight route
        for intermediate in intermediate_airports + [destination_airport]:
            intermediate_flight_route = self.find_shortest_distance(current_source, intermediate)
            if intermediate_flight_route is None:
                # No valid route found for this segment, return None
                return None
            else:
                flight_path.extend(intermediate_flight_route["path"][1:])
                multi_flight_segments.extend(intermediate_flight_route["segments"])
                total_layover_time += intermediate_flight_route["total_layover_time"]
                current_source = intermediate

        # Process multi-flight route information
        total_stops = len(multi_flight_segments)
        total_cost = sum(segment["cost"] for segment in multi_flight_segments)
        total_duration = sum(segment["duration"] for segment in multi_flight_segments)

        # Return aggregated information for the multi-flight route
        return {
            "path": flight_path,
            "segments": multi_flight_segments,
            "total_stops": total_stops,
            "total_cost": total_cost,
            "total_duration": total_duration,
            "total_layover_time": total_layover_time
        }

    def find_least_cost(self, source_airport, destination_airport):
        """
            Find the path that costs the least between two airports using Dijkstra's shortest path algorithm.

            Args:
                source_airport (str): The IATA code of the source airport.
                destination_airport (str): The IATA code of the destination airport.

            Returns:
                dict or None: A dictionary containing information about the shortest distance route,
                              including the flight path, segments, total stops, total cost, total duration,
                              and total layover time. Returns None if no valid route is found.
        """
        # Check if flight data from source airport exist in the graph
        if not self.graph.get_routes(source_airport):
            print(f"Flights from '{source_airport}' do not exist.")
            return None

        # Check if flight data to destination airport exist in the graph
        if not self.graph.get_routes_to(destination_airport):
            print(f"Flights to '{destination_airport}' do not exist")
            # Find the nearest airport to the destination recursively
            nearest_airport = self.graph.find_nearest_airport(destination_airport)
            print(f"Rerouting to nearest airport {nearest_airport}.")

            # Check if the nearest airports has routes to it
            if nearest_airport is None or not self.graph.get_routes_to(nearest_airport):
                print(f"No flights to {nearest_airport}.")
                return None

            destination_airport = nearest_airport

            # Restart the search from the source airport to the nearest airport
            return self.find_least_cost(source_airport, destination_airport)

        # Clear shortest path memory
        costs = {}
        previous_airport = {}  # Initialize a dictionary to store the previous airport for each airport

        # Initialize cost to all airports as infinity
        costs = {airport: float('inf') for airport in self.graph.airports}
        costs[source_airport] = 0

        # Initialize priority queue with a simple list
        priority_queue = [(0, source_airport)]

        while priority_queue:
            current_cost, current_airport = heapq.heappop(priority_queue)

            # If the destination airport is reached, stop
            if current_airport == destination_airport:
                break

            # Visit each neighboring airport of the current airport
            for neighbour in self.graph.get_neighbors(current_airport):
                cost_to_neighbour = current_cost + self.graph.get_flight_cost(current_airport, neighbour)
                # Update the cost to the neighbor if it's smaller than the recorded cost
                if cost_to_neighbour < costs[neighbour]:
                    costs[neighbour] = cost_to_neighbour
                    #  Update the path taken
                    previous_airport[neighbour] = current_airport
                    heapq.heappush(priority_queue, (cost_to_neighbour, neighbour))

        # Reconstruct the shortest path from the previous_airport dictionary
        shortest_path = []
        current_airport = destination_airport
        while current_airport != source_airport:
            shortest_path.append(current_airport)
            current_airport = previous_airport[current_airport]
        shortest_path.append(source_airport)

        # Reverse the path to get it in the correct order
        shortest_path.reverse()

        # Get route information
        route = self.graph.get_route_information(shortest_path)

        # Return the route information
        return route

    def find_least_cost_multi(self, source_airport, destination_airport, intermediate_airports):
        """
            Find the least cost multi-flight route between two airports with intermediate stops.

            Args:
                source_airport (str): The IATA code of the source airport.
                destination_airport (str): The IATA code of the destination airport.
                intermediate_airports (list of str): List of IATA codes of intermediate airports.

            Returns:
                dict or None: A dictionary containing information about the shortest distance multi-flight route,
                              including the flight path, segments, total stops, total cost, total duration,
                              and total layover time. Returns None if no valid route is found.
        """
        # Initialize variables
        multi_flight_segments = []
        current_source = source_airport
        flight_path = [current_source]
        total_layover_time = 0

        # Find the shortest distance for each segment of the multi-flight route
        for intermediate in intermediate_airports + [destination_airport]:
            intermediate_flight_route = self.find_least_cost(current_source, intermediate)
            if intermediate_flight_route is None:
                # No valid route found for this segment, return None
                return None
            else:
                flight_path.extend(intermediate_flight_route["path"][1:])
                multi_flight_segments.extend(intermediate_flight_route["segments"])
                total_layover_time += intermediate_flight_route["total_layover_time"]
                current_source = intermediate

        # Process multi-flight route information
        total_stops = len(multi_flight_segments)
        total_cost = sum(segment["cost"] for segment in multi_flight_segments)
        total_duration = sum(segment["duration"] for segment in multi_flight_segments)

        # Return aggregated information for the multi-flight route
        return {
            "path": flight_path,
            "segments": multi_flight_segments,
            "total_stops": total_stops,
            "total_cost": total_cost,
            "total_duration": total_duration,
            "total_layover_time": total_layover_time
        }

    def find_shortest_duration(self, source_airport, destination_airport):
        """
            Find the shortest duration path between two airports using Dijkstra's shortest path algorithm.

            Args:
                source_airport (str): The IATA code of the source airport.
                destination_airport (str): The IATA code of the destination airport.

            Returns:
                dict or None: A dictionary containing information about the shortest distance route,
                              including the flight path, segments, total stops, total cost, total duration,
                              and total layover time. Returns None if no valid route is found.
        """
        # Check if flight data from source airport exist in the graph
        if not self.graph.get_routes(source_airport):
            print(f"Flights from '{source_airport}' do not exist.")
            return None

        # Check if flight data to destination airport exist in the graph
        if not self.graph.get_routes_to(destination_airport):
            print(f"Flights to '{destination_airport}' do not exist")
            # Find the nearest airport to the destination recursively
            nearest_airport = self.graph.find_nearest_airport(destination_airport)
            print(f"Rerouting to nearest airport {nearest_airport}.")

            # Check if the nearest airports has routes to it
            if nearest_airport is None or not self.graph.get_routes_to(nearest_airport):
                print(f"No flights to {nearest_airport}.")
                return None

            destination_airport = nearest_airport

            # Restart the search from the source airport to the nearest airport
            return self.find_shortest_duration(source_airport, destination_airport)

        # Clear shortest path memory
        durations = {}
        previous_airport = {}  # Initialize a dictionary to store the previous airport for each airport

        # Initialize cost to all airports as infinity
        durations = {airport: float('inf') for airport in self.graph.airports}
        durations[source_airport] = 0

        # Initialize priority queue with a simple list
        priority_queue = [(0, source_airport)]

        while priority_queue:
            current_duration, current_airport = heapq.heappop(priority_queue)

            # If the destination airport is reached, stop
            if current_airport == destination_airport:
                break

            # Visit each neighboring airport of the current airport
            for neighbour in self.graph.get_neighbors(current_airport):
                time_to_neighbour = current_duration + self.graph.get_flight_duration(current_airport, neighbour)

                if neighbour != destination_airport:
                    time_to_neighbour += 2  # Add 2 hours for layover time

                # Update the time to the neighbor if it's smaller than the recorded duration
                if time_to_neighbour < durations[neighbour]:
                    durations[neighbour] = time_to_neighbour
                    #  Update the path taken
                    previous_airport[neighbour] = current_airport
                    heapq.heappush(priority_queue, (time_to_neighbour, neighbour))

        # Reconstruct the shortest path from the previous_airport dictionary
        shortest_path = []
        current_airport = destination_airport
        while current_airport != source_airport:
            shortest_path.append(current_airport)
            current_airport = previous_airport[current_airport]
        shortest_path.append(source_airport)

        # Reverse the path to get it in the correct order
        shortest_path.reverse()

        # Get the route information
        route = self.graph.get_route_information(shortest_path)

        # Return the route information
        return route

    def find_shortest_duration_multi(self, source_airport, destination_airport, intermediate_airports):
        # Initialize variables
        multi_flight_segments = []
        current_source = source_airport
        flight_path = [current_source]
        total_layover_time = 0

        # Find the shortest distance for each segment of the multi-flight route
        for intermediate in intermediate_airports + [destination_airport]:
            intermediate_flight_route = self.find_shortest_duration(current_source, intermediate)
            if intermediate_flight_route is None:
                # No valid route found for this segment, return None
                return None
            else:
                flight_path.extend(intermediate_flight_route["path"][1:])
                multi_flight_segments.extend(intermediate_flight_route["segments"])
                total_layover_time += intermediate_flight_route["total_layover_time"]
                current_source = intermediate

        # Process multi-flight route information
        total_stops = len(multi_flight_segments)
        total_cost = sum(segment["cost"] for segment in multi_flight_segments)
        total_duration = sum(segment["duration"] for segment in multi_flight_segments)

        # Return aggregated information for the multi-flight route
        return {
            "path": flight_path,
            "segments": multi_flight_segments,
            "total_stops": total_stops,
            "total_cost": total_cost,
            "total_duration": total_duration,
            "total_layover_time": total_layover_time
        }


class BFS:
    def __init__(self, graph):
        self.graph = graph

        # Function to perform Breadth First Search on the flight graph to return path with the least route edges

    def find_least_layovers(self, source_airport, destination_airport):
        # Create a queue for BFS
        queue = deque()
        visited = set()

        previous_airport = {}  # Initialize a dictionary to store the previous airport for each airport

        # Mark the source airport as visited and enqueue it along with the initial layover count of 0
        queue.append(source_airport)
        visited.add(source_airport)

        # Iterate over the queue
        while queue:
            # Dequeue a vertex from the queue
            current_airport = queue.popleft()

            # If current airport is the destination, stop
            if current_airport == destination_airport:
                break

            # Visit each neighboring airport of the current airport
            for neighbour in self.graph.get_neighbors(current_airport):
                if neighbour not in visited:
                    #  Update the path taken
                    previous_airport[neighbour] = current_airport
                    visited.add(neighbour)
                    queue.append(neighbour)

        # If the destination airport is not visited, it means it is not reachable
        if destination_airport not in visited:
            print(f"No flights from {source_airport} to {destination_airport}.")
            # Find the nearest airport to the destination recursively
            nearest_airport = self.graph.find_nearest_airport(destination_airport)
            print(f"Rerouting to nearest airport {nearest_airport}.")

            # Check if the nearest airport has routes to it
            if nearest_airport is None or not self.graph.get_routes_to(nearest_airport):
                print(f"No flights to {nearest_airport}.")
                return None

            destination_airport = nearest_airport

            # Restart the search from the source airport to the nearest airport
            return self.find_least_layovers(source_airport, destination_airport)

        # Reconstruct the shortest path from the previous_airport dictionary
        shortest_path = []
        current_airport = destination_airport
        while current_airport != source_airport:
            shortest_path.append(current_airport)
            current_airport = previous_airport[current_airport]
        shortest_path.append(source_airport)

        # Reverse the path to get it in the correct order
        shortest_path.reverse()

        route = self.graph.get_route_information(shortest_path)

        return route

    def find_least_layovers_multi(self, source_airport, destination_airport, intermediate_airports):
        """
            Find the least layovers multi-flight route between two airports with intermediate stops.

            Args:
                source_airport (str): The IATA code of the source airport.
                destination_airport (str): The IATA code of the destination airport.
                intermediate_airports (list of str): List of IATA codes of intermediate airports.

            Returns:
                dict or None: A dictionary containing information about the shortest distance multi-flight route,
                              including the flight path, segments, total stops, total cost, total duration,
                              and total layover time. Returns None if no valid route is found.
        """
        # Initialize variables
        multi_flight_segments = []
        current_source = source_airport
        flight_path = [current_source]
        total_layover_time = 0

        # Find the shortest distance for each segment of the multi-flight route
        for intermediate in intermediate_airports + [destination_airport]:
            intermediate_flight_route = self.find_least_layovers(current_source, intermediate)
            if intermediate_flight_route is None:
                # No valid route found for this segment, return None
                return None
            else:
                flight_path.extend(intermediate_flight_route["path"][1:])
                multi_flight_segments.extend(intermediate_flight_route["segments"])
                total_layover_time += intermediate_flight_route["total_layover_time"]
                current_source = intermediate

        # Process multi-flight route information
        total_stops = len(multi_flight_segments)
        total_cost = sum(segment["cost"] for segment in multi_flight_segments)
        total_duration = sum(segment["duration"] for segment in multi_flight_segments)

        # Return aggregated information for the multi-flight route
        return {
            "path": flight_path,
            "segments": multi_flight_segments,
            "total_stops": total_stops,
            "total_cost": total_cost,
            "total_duration": total_duration,
            "total_layover_time": total_layover_time
        }


class AStar:
    def __init__(self, graph):
        self.graph = graph

    def find_optimal_flight(self, source_airport, destination_airport):
        # Check if flight data from source airport exist in the graph
        if not self.graph.get_routes(source_airport):
            print(f"Flights from '{source_airport}' do not exist.")
            return None

        if not self.graph.get_routes_to(destination_airport):
            print(f"Flights to '{destination_airport}' do not exist")
            # Find the nearest airport to the destination recursively
            nearest_airport = self.graph.find_nearest_airport(destination_airport)
            print(f"Rerouting to nearest airport {nearest_airport}.")

            # Check if the nearest airports has routes to it
            if nearest_airport is None or not self.graph.get_routes_to(nearest_airport):
                print(f"No flights to {nearest_airport}.")
                return None

            destination_airport = nearest_airport

            # Restart the search from the source airport to the nearest airport
            return self.find_optimal_flight(source_airport, destination_airport)

        # Initialize a dictionary to store the previous airport for each airport
        previous_airport = {}

        # Dict to store the actual cost from source to each node
        g_score = {iata: float('inf') for iata in self.graph.airports}
        g_score[source_airport] = 0

        # Initialize priority queue with a simple list
        priority_queue = [(0, source_airport)]

        while priority_queue:
            current_cost, current_airport = heapq.heappop(priority_queue)

            # If the destination airport is reached, stop
            if current_airport == destination_airport:
                break

            # Visit each neighboring airport of the current airport
            for neighbour in self.graph.get_neighbors(current_airport):
                tentative_g_score = current_cost + self.graph.calculate_distance(current_airport, neighbour)
                # Update the distance to the neighbor if it's smaller than the recorded distance
                if tentative_g_score < g_score[neighbour]:
                    g_score[neighbour] = tentative_g_score
                    # Calculate the estimated total cost from the source to the destination through the neighbor
                    # (using the heuristic, which is the estimated flight cost and duration in this case)
                    cost_score = self.graph.get_flight_cost(current_airport, neighbour)
                    duration_score = self.graph.get_flight_duration(current_airport, neighbour)
                    if neighbour != destination_airport:
                        duration_score += 2
                    h_score = cost_score + duration_score
                    f_score = tentative_g_score + h_score
                    # Update the path taken
                    previous_airport[neighbour] = current_airport
                    heapq.heappush(priority_queue, (f_score, neighbour))

        # Reconstruct the shortest path from the previous_airport dictionary
        shortest_path = []
        current_airport = destination_airport
        while current_airport != source_airport:
            shortest_path.append(current_airport)
            current_airport = previous_airport[current_airport]
        shortest_path.append(source_airport)

        shortest_path.reverse()

        route = self.graph.get_route_information(shortest_path)

        return route

    def find_optimal_flight_multi(self, source_airport, destination_airport, intermediate_airports):
        # Initialize variables
        multi_flight_segments = []
        current_source = source_airport
        flight_path = [current_source]
        total_layover_time = 0

        # Find the shortest distance for each segment of the multi-flight route
        for intermediate in intermediate_airports + [destination_airport]:
            intermediate_flight_route = self.find_optimal_flight(current_source, intermediate)
            if intermediate_flight_route is None:
                # No valid route found for this segment, return None
                return None
            else:
                flight_path.extend(intermediate_flight_route["path"][1:])
                multi_flight_segments.extend(intermediate_flight_route["segments"])
                total_layover_time += intermediate_flight_route["total_layover_time"]
                current_source = intermediate

        # Process multi-flight route information
        total_stops = len(multi_flight_segments)
        total_cost = sum(segment["cost"] for segment in multi_flight_segments)
        total_duration = sum(segment["duration"] for segment in multi_flight_segments)

        # Return aggregated information for the multi-flight route
        return {
            "path": flight_path,
            "segments": multi_flight_segments,
            "total_stops": total_stops,
            "total_cost": total_cost,
            "total_duration": total_duration,
            "total_layover_time": total_layover_time
        }
