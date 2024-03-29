from math import radians, sin, cos, asin, sqrt, ceil


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


def calculate_flight_duration(distance):
    """Calculates the estimated flight duration in hours based on distance.

    This function provides a basic estimate of flight duration by considering:
        - A base_duration to account for pre-flight and taxiing time.
        - An average flight speed.

    **Parameters:**

        distance (float): The distance of the flight in kilometers.

    **Returns:**

        float: The estimated flight duration in hours.

    **Assumptions:**

        - This is a simplified calculation and does not account for factors like wind speed,
          altitude, or specific aircraft performance.
        - The base_duration is an estimate and may vary depending on the airport and flight.
    """

    base_duration = 1  # Hours to account for pre-flight/taxiing (adjust if needed)
    flight_speed = 800  # Average flight speed (km/h) - adjust for a more accurate estimate

    # Calculate total flight time based on distance and average speed
    flight_duration = base_duration + (distance / flight_speed)

    return flight_duration


def format_duration(duration):
    # get the hours and minutes taken
    hours = int(duration)
    minutes = int((duration - hours) * 60)

    # format duration in HH:MM format
    duration_formatted = f"{hours:02d}:{minutes:02d}"

    return duration_formatted
