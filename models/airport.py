from models.route import RouteEdge


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
