import os 
from dotenv import load_dotenv 
from supabase import create_client, Client

class DatabaseClient:
    def __init__(self):
        load_dotenv()
        SUPABASE_URL: str = os.getenv("SUPABASE_URL")
        SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

        # Create a Supabase client instance.
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def add_location(self, name: str, lat: float, lng: float) -> dict:
        data_payload = {
            "name": name,
            "lat": lat,
            "lng": lng
        }
        
        response = self.supabase.table("locations").insert(data_payload).execute()
        return response.data
  
    def get_locations(self) -> dict:
        response = self.supabase.table("locations").select("*").execute()
        return response.data
    
    def get_food_items(self, location_id: int) -> dict:
        response = self.supabase.table("food_item").select("*").eq("locationId", location_id).execute()
        return response.data

    def get_nearby_locations(self, user_lat: float, user_lon: float, search_radius_meters: float):
        payload = {
            "query_lat": user_lat,
            "query_lon": user_lon,
            "radius_meters": search_radius_meters
        }
        
        response = self.supabase.rpc("get_nearby_locations", payload).execute()
        
        return response.data

    def add_food_item(
        self,
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
        
        response = self.supabase.table("food_item").insert(data_payload).execute()
        return response.data

# Example usage:
if __name__ == "__main__":
    db_client = DatabaseClient()
    
    locations = db_client.get_locations()
    print(locations)
    
    food_items = db_client.get_food_items(1)
    print(food_items)
    
    # Example parameters (adjust as needed)
    sample_user_lat = -90.0   # example latitude
    sample_user_lon = -90.0   # example longitude
    sample_radius = 5000      # 5 km radius



    # data = db_client.get_nearby_locations(sample_user_lat, sample_user_lon, sample_radius)
    
    # if data is not None:
    #     print("Nearest locations:", data)
    # else:
    #     print("No data found or there was an error.")
    # # add_record("Wendys", 40.7128, 74.0060, ["burger", "fries"], False, False, False, False, False, False, False)
    # new_food = db_client.add_food_item(
    #     name="Cheeseburger",
    #     description="A delicious cheeseburger with fresh ingredients.",
    #     gluten_free=False,
    #     vegan=False,
    #     vegetarian=False,
    #     halal=True,
    #     kosher=False,
    #     locationId=1
    # )
    # print("Inserted food item:", new_food)