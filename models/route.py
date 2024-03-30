class RouteEdge:
    def __init__(self, source_airport, destination_airport, weights):
        # The IATA code of the source airport where the flight originates.
        self.source_airport = source_airport
        # The IATA code of the destination airport where the flight ends.
        self.destination_airport = destination_airport
        # A dictionary containing weights associated with the flight route, such as distance, cost, and duration.
        self.weights = weights

    def get_weight(self, weight_name):
        return self.weights.get(weight_name)
