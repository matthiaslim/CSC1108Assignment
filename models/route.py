class RouteEdge:
    def __init__(self, source_airport, destination_airport, weights):
        self.source_airport = source_airport
        self.destination_airport = destination_airport
        self.weights = weights  # Dictionary to store weights

    def get_weight(self, weight_name):
        return self.weights.get(weight_name)
