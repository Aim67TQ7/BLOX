import { Client } from "@googlemaps/google-maps-services-js";

type DistanceMatrixResponse = {
  rows: Array<{
    elements: Array<{
      distance: { value: number };
    }>;
  }>;
};

async function getDistanceMatrix(apiKey: string, locations: string[]): Promise<DistanceMatrixResponse> {
  /**
   * Get the distance matrix between locations using Google Maps API.
   */
  const client = new Client({});
  const response = await client.distancematrix({
    params: {
      origins: locations,
      destinations: locations,
      mode: "driving",
      key: apiKey,
    },
  });

  return response.data as DistanceMatrixResponse;
}

function calculateBestRoute(distanceMatrix: DistanceMatrixResponse, locations: string[]): { bestRoute: string[]; shortestDistance: number } {
  /**
   * Determine the best route (shortest) between the given locations.
   */
  // Extract distance information
  const distances = distanceMatrix.rows.map((row) =>
    row.elements.map((element) => element.distance.value)
  );

  // Get all permutations of the locations
  const permutations = permute(Array.from({ length: locations.length }, (_, i) => i));

  let bestRoute: number[] | null = null;
  let shortestDistance = Infinity;

  // Calculate the total distance for each route permutation
  for (const perm of permutations) {
    let totalDistance = 0;
    for (let i = 0; i < perm.length - 1; i++) {
      totalDistance += distances[perm[i]][perm[i + 1]];
    }

    // Update the best route if the total distance is shorter
    if (totalDistance < shortestDistance) {
      shortestDistance = totalDistance;
      bestRoute = perm;
    }
  }

  // Convert indices back to location names
  const bestRouteLocations = bestRoute!.map((index) => locations[index]);
  return { bestRoute: bestRouteLocations, shortestDistance };
}

function permute(array: number[]): number[][] {
  /**
   * Generate all permutations of an array.
   */
  if (array.length === 0) return [[]];

  const result: number[][] = [];
  for (let i = 0; i < array.length; i++) {
    const rest = permute(array.slice(0, i).concat(array.slice(i + 1)));
    for (const r of rest) {
      result.push([array[i], ...r]);
    }
  }

  return result;
}

async function main() {
  // Input Google Maps API key
  const apiKey = prompt("Enter your Google Maps API key:") || "";

  // Input locations
  console.log("Enter between 2 and 10 locations (type 'done' when finished):");
  const locations: string[] = [];
  while (locations.length < 10) {
    const location = prompt(`Location ${locations.length + 1}:`)?.trim();
    if (location?.toLowerCase() === "done") {
      if (locations.length >= 2) break;
      console.log("Please enter at least two locations.");
      continue;
    }
    if (location) locations.push(location);
  }

  if (locations.length < 2) {
    console.log("You need at least two locations to calculate a route.");
    return;
  }

  try {
    // Get the distance matrix
    const distanceMatrix = await getDistanceMatrix(apiKey, locations);

    // Calculate the best route
    const { bestRoute, shortestDistance } = calculateBestRoute(distanceMatrix, locations);

    // Display the results
    console.log("\nBest Route:");
    bestRoute.forEach((loc, i) => {
      console.log(`${i + 1}: ${loc}`);
    });
    console.log(`\nTotal Distance: ${(shortestDistance / 1000).toFixed(2)} km`);
  } catch (error) {
    console.error(`An error occurred: ${error}`);
  }
}

main();
