import os 
from dotenv import load_dotenv 
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

# Create a Supabase client instance.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_location(
    name: str,
    lat: float,
    lng: float
) -> dict:

    data_payload = {
        "name": name,
        "lat": lat,
        "lng": lng
    }
    
    response = supabase.table("locations").insert(data_payload).execute()
    
    return response.data

def get_nearby_locations(user_lat: float, user_lon: float, search_radius_meters: float):
    payload = {
        "query_lat": user_lat,
        "query_lon": user_lon,
        "radius_meters": search_radius_meters
    }
    
    response = supabase.rpc("get_nearby_locations", payload).execute()
    
    # if response.error:
    #     print("Error fetching nearest locations:", response.error.message)
    #     return None
    
    return response.data

def add_food_item (
    name: str,
    description: str,
    gluten_free: bool,
    vegan: bool,
    vegetarian: bool,
    halal: bool,
    kosher: bool,
    locationId: int
) -> dict:
    data_payload = {
        "name": name,
        "description": description,
        "gluten_free": gluten_free,
        "vegan": vegan,
        "vegetarian": vegetarian,
        "halal": halal,
        "kosher": kosher,
        "locationId": locationId
    }
    
    response = supabase.table("food_item").insert(data_payload).execute()
    
    return response.data

# Example usage:
if __name__ == "__main__":
    # # Example parameters (adjust as needed)
    sample_user_lat = -90.0   # example latitude
    sample_user_lon = -90.0   # example longitude
    sample_radius = 5000      # 5 km radius

    data = get_nearby_locations(sample_user_lat, sample_user_lon, sample_radius)
    
    if data is not None:
        print("Nearest locations:", data)
    else:
        print("No data found or there was an error.")
    # add_record("Wendys", 40.7128, 74.0060, ["burger", "fries"], False, False, False, False, False, False, False)
    new_food = add_food_item(
        name="Cheeseburger",
        description="A delicious cheeseburger with fresh ingredients.",
        gluten_free=False,
        vegan=False,
        vegetarian=False,
        halal=True,
        kosher=False,
        locationId=1
    )
    print("Inserted food item:", new_food)