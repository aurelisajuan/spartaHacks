from typing import Any, Dict, Callable
from swarm.types import Result
import logging
from util import get_geocode
from generator import generate_sql_query, fetch_db


def convert_address_to_coords(address: str) -> Result:
    """Call this function when the user supplies an address or location."""
    logging.info(f"Converting address to coordinates for: {address}")
    print("Ok let me just check your current location.")

    # call google geocode
    coords = get_geocode(address)
    logging.info(f"Converted address '{address}' to coordinates: {coords}")
    return "Converted address '{address}' to coordinates: {coords}".format(
        address=address, coords=coords
    )


def query_db(query: str) -> Result:
    """Call this function to query the database for supplier options once the user supplied a location and dietary restrictions. ."""
    sql_query = generate_sql_query(query)
    print("SQL Query: ", sql_query)
    logging.info(f"Querying database with query: {sql_query}")
    results = fetch_db(sql_query)
    logging.info(f"Found these results: {results}")
    # results = [
    #     {
    #         "name": "Food Bank NYC",
    #         "address": "123 Main St, New York, NY",
    #         "distance": "0.5 miles",
    #         "dietary_options": ["halal", "kosher", "vegetarian"]
    #     },
    #     {
    #         "name": "Community Kitchen",
    #         "address": "456 Broadway, New York, NY",
    #         "distance": "1.2 miles",
    #         "dietary_options": ["vegan", "gluten-free"]
    #     },
    #     {
    #         "name": "Local Pantry",
    #         "address": "789 Park Ave, New York, NY",
    #         "distance": "2.1 miles",
    #         "dietary_options": ["halal", "vegetarian"]
    #     }
    # ]
    return "I found the following restaurants: " + str(results)
