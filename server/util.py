import os
from dotenv import load_dotenv
import requests

load_dotenv(override=True)

def get_geocode(address: str) -> dict:
    """
    Given an address string, this function fetches its geocode information from the Google Maps Geocoding API.
    
    :param address: The address to geocode.
    :return: A dictionary containing 'lat' and 'lng' if successful.
    :raises Exception: If the network request fails or the API returns an error.
    """
    # URL-encode the address
    encoded_address = requests.utils.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={os.getenv("PLACES_API_KEY")}"

    # Make the GET request to the Google Maps Geocoding API
    response = requests.get(url)
    
    # Check if the HTTP request was successful
    if not response.ok:
        raise Exception(f"Network error: {response.status_code} {response.reason}")
    
    # Parse the JSON response
    data = response.json()
    
    # Check if the API returned a successful status and results are available
    if data.get("status") != "OK" or not data.get("results"):
        raise Exception(f"Geocoding API error: {data.get('status')}")
    
    # Extract the location from the first result
    location = data["results"][0]["geometry"]["location"]
    return {
        "lat": location["lat"],
        "lng": location["lng"]
    }

# Example usage:
if __name__ == "__main__":
    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    try:
        coordinates = get_geocode(address)
        print(f"Latitude: {coordinates['lat']}, Longitude: {coordinates['lng']}")
    except Exception as e:
        print(f"Error geocoding address: {e}")
