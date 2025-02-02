import os 
from supabase import create_client, Client

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

supabase: Client = create_client(url, key)

from supabase import create_client, Client

# Replace with your actual Supabase project details.
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"

# Create a Supabase client instance.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def add_record(
    name: str,
    lat: float,
    lng: float,
    inventory: list,
    vegetarian: bool,
    vegan: bool,
    dairy: bool,
    gluten: bool,
    halal: bool,
    kosher: bool,
    nuts: bool
) -> dict:

    data_payload = {
        "name": name,
        "lat": lat,
        "lng": lng,
        "inventory": inventory,
        "vegetarian": vegetarian,
        "vegan": vegan,
        "dairy": dairy,
        "gluten": gluten,
        "halal": halal,
        "kosher": kosher,
        "nuts": nuts,
    }
    
    response = supabase.table("location").insert(data_payload).execute()
    
    return response.data
