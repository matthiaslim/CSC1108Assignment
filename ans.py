{
    "path": [   # List of airports in the route
        "Airport1",
        "Airport2",
        ...
        "DestinationAirport"
    ],
    "segments": [   # List of segments, each representing a flight or layover
        {
            "from": "Airport1",
            "to": "Airport2",
            "cost": 100,   # Cost of the flight segment
            "duration": 2,   # Duration of the flight segment in hours
            "layover": 0   # Layover time in hours (0 for flight segments)
        },
        {
            "from": "Airport2",
            "to": "Airport3",
            "cost": 150,
            "duration": 1.5,
            "layover": 2   # Layover time between flights
        },
        ...
    ],
    "total_stops": 2,   # Total number of stops (layovers)
    "total_cost": 250,   # Total cost of the entire route
    "total_duration": 5,   # Total duration of the entire route in hours
    "total_layover_time": 4   # Total layover time in hours for the entire route
}
