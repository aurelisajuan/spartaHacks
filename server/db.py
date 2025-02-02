import os
from dotenv import load_dotenv
from supabase import create_client, Client
from util import get_geocode


class DatabaseClient:
    def __init__(self):
        load_dotenv()
        SUPABASE_URL: str = os.getenv("SUPABASE_URL")
        SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Missing SUPABASE_URL or SUPABASE_KEY environment variables"
            )
            print("Error:", e)

        # Create a Supabase client instance.
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Database client initialized", self.supabase)

    def add_location(self, name: str, address: str) -> dict:
        coordinates = get_geocode(address)
        data_payload = {
            "name": name,
            "lat": coordinates["lat"],
            "lng": coordinates["lng"],
        }

        response = self.supabase.table("locations").insert(data_payload).execute()
        return response.data

    def get_locations(self) -> dict:
        response = self.supabase.table("locations").select("*").execute()
        return response.data

    def get_food_items(self, location_id: int) -> dict:
        response = (
            self.supabase.table("food_item")
            .select("*")
            .eq("location_id", location_id)
            .execute()
        )
        return response.data

    def get_nearby_locations(
        self, user_lat: float, user_lon: float, search_radius_meters: float
    ):
        payload = {
            "query_lat": user_lat,
            "query_lon": user_lon,
            "radius_meters": search_radius_meters,
        }

        response = self.supabase.rpc("get_nearby_locations", payload).execute()

        return response.data

    def get_nearby_dietary_locations(
        self,
        user_lat: float,
        user_lon: float,
        search_radius_meters: float,
        gluten_free: bool,
        vegan: bool,
        vegetarian: bool,
        halal: bool,
        kosher: bool,
    ):
        payload = {
            "user_lat": user_lat,
            "user_lon": user_lon,
            "search_radius_meters": search_radius_meters,
            "want_gluten_free": gluten_free,
            "want_vegan": vegan,
            "want_vegetarian": vegetarian,
            "want_halal": halal,
            "want_kosher": kosher,
        }

        response = self.supabase.rpc(
            "find_nearest_locations_with_diet", payload
        ).execute()
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
        location_id: int,
    ) -> dict:
        data_payload = {
            "name": name,
            "description": description,
            "gluten_free": gluten_free,
            "vegan": vegan,
            "vegetarian": vegetarian,
            "halal": halal,
            "kosher": kosher,
            "location_id": location_id,
        }

        response = self.supabase.table("food_item").insert(data_payload).execute()
        return response.data

    def add_call(self, title: str, food_items: str, transcript: str) -> dict:
        data_payload = {
            "title": title,
            "food_items": food_items,
            "transcript": transcript,
        }

        response = self.supabase.table("call").insert(data_payload).execute()
        return response.data

    def get_call(self, call_id: int) -> dict:
        response = self.supabase.table("call").select("*").eq("id", call_id).execute()
        return response.data

    def upsert_call(
        self,
        call_id: int,
        transcript: str | None,
        title: str | None = None,
        food_items: str | None = None,
    ) -> dict:
        try:
            data_payload = {
                "id": call_id,
                "title": title if title else "In Progress Call",
                "food_items": food_items if food_items else "",
                "transcript": transcript if transcript else [],
            }

            response = self.supabase.table("call").upsert(data_payload).execute()
            return response.data
        except Exception as e:
            print("Error upserting call:", e)
            return None


# Example usage:
if __name__ == "__main__":
    db_client = DatabaseClient()

    upsert_call = db_client.upsert_call(1, "bill", "HI", "BYE")
    print("Upserted call record:", upsert_call)

    # # Example parameters (adjust as needed)
    # sample_user_lat = -90.0   # example latitude
    # sample_user_lon = -90.0   # example longitude
    # sample_radius = 5000      # 5 km radius

    # dietary_locations = db_client.get_nearby_dietary_locations(sample_user_lat, sample_user_lon, sample_radius, False, False, False, False, False)
    # print(dietary_locations)

    # new_call = db_client.add_call("WARREN", "blabakbababhl", "saasdfasf")
    # print("Added call record:", new_call)

    # # Check if a record was inserted and has an ID
    # if new_call and isinstance(new_call, list) and "id" in new_call[0]:
    #     call_id = new_call[0]["id"]
    #     print(f"Retrieving call with ID: {call_id}")

    #     # Retrieve the call record by ID
    #     retrieved_call = db_client.get_call(call_id)
    #     print("Retrieved call record:", retrieved_call)
    # else:
    #     print("Error: Call record was not added correctly or no ID was returned.")

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
