import googlemaps
import itertools

def get_distance_matrix(api_key, locations):
    """
    Get the distance matrix between locations using Google Maps API.
    """
    gmaps = googlemaps.Client(key=api_key)
    matrix = gmaps.distance_matrix(locations, locations, mode="driving")
    return matrix

def calculate_best_route(distance_matrix, locations):
    """
    Determine the best route (shortest) between the given locations.
    """
    # Extract distance information
    distances = [
        [row["elements"][j]["distance"]["value"] for j in range(len(row["elements"]))]
        for row in distance_matrix["rows"]
    ]

    # Get all permutations of the locations
    permutations = list(itertools.permutations(range(len(locations))))

    best_route = None
    shortest_distance = float("inf")

    # Calculate the total distance for each route permutation
    for perm in permutations:
        total_distance = 0
        for i in range(len(perm) - 1):
            total_distance += distances[perm[i]][perm[i + 1]]

        # Update the best route if the total distance is shorter
        if total_distance < shortest_distance:
            shortest_distance = total_distance
            best_route = perm

    # Convert indices back to location names
    best_route_locations = [locations[i] for i in best_route]
    return best_route_locations, shortest_distance

if __name__ == "__main__":
    # Input Google Maps API key
    API_KEY = input("Enter your Google Maps API key: ")

    # Input locations
    print("Enter between 2 and 10 locations (type 'done' when finished):")
    locations = []
    while len(locations) < 10:
        location = input(f"Location {len(locations) + 1}: ").strip()
        if location.lower() == 'done':
            if len(locations) >= 2:
                break
            else:
                print("Please enter at least two locations.")
                continue
        locations.append(location)

    if len(locations) < 2:
        print("You need at least two locations to calculate a route.")
    else:
        # Get the distance matrix
        try:
            distance_matrix = get_distance_matrix(API_KEY, locations)

            # Calculate the best route
            best_route, shortest_distance = calculate_best_route(distance_matrix, locations)

            # Display the results
            print("\nBest Route:")
            for i, loc in enumerate(best_route):
                print(f"{i + 1}: {loc}")
            print(f"\nTotal Distance: {shortest_distance / 1000:.2f} km")

        except Exception as e:
            print(f"An error occurred: {e}")
