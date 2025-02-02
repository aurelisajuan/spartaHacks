from dotenv import load_dotenv
import os
import openai
import psycopg2
import json

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Updated URI with SSL and disabled GSSAPI
uri = f"postgresql://postgres.vspiducqotienguaopyc:{DB_PASSWORD}@aws-0-us-west-1.pooler.supabase.com:6543/postgres?sslmode=require&gssencmode=disable"

openai.api_key = OPENAI_API_KEY


def generate_sql_query(conversation) -> str:
    system_prompt = """
You are a data-management agent tasked with generating valid PostgreSQL SQL statements
based on a specified schema, user location references, dietary preferences, and conversation context.

Here is the database schema:

Table: locations
  - id: int
  - created_at: timestamp
  - name: text
  - lat: float8
  - lng: float8

Table: food_item
  - id: int
  - created_at: timestamp
  - name: text
  - description: text
  - gluten_free: boolean
  - vegan: boolean
  - vegetarian: boolean
  - kosher: boolean
  - type: enum("meat", "dairy", "produce", "grains", "prepared")
  - location_id: int (foreign key referencing locations.id)

When the user references any of the following dietary restrictions:
 - gluten_free
 - vegan
 - vegetarian
 - kosher
 - halal

Create an explicit filter in the WHERE clause, for example:
   WHERE gluten_free = TRUE (if user asked for gluten-free)
If the user does not mention a given restriction, do NOT filter on that column.

When the user requests cardinal directions:
 - "east of me": location.lng > user_lng
 - "west of me": location.lng < user_lng
 - "north of me": location.lat > user_lat
 - "south of me": location.lat < user_lat

For "within some distance of me," consider using a distance formula (e.g., Haversine) or bounding box in WHERE.
If the user does not specify a particular filter or direction, leave it out.

NEVER include data from the food_item table in your query.

Output only the final SQL query. No additional text.
"""
    user_prompt = f"""
User conversation (condensed/filtered):
{conversation}

Generate the final SQL query now.
"""
    response = openai.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        reasoning_effort="low",
    )
    sql_query = response.choices[0].message.content
    if "```sql" in sql_query:
        sql_query = sql_query.split("```sql")[1].split("```")[0]
    return sql_query.strip()


def generate_sql_insert(conversation) -> str:
    system_prompt = """
You are a data-management agent tasked with generating valid PostgreSQL SQL statements
based on a specified schema, user location references, dietary preferences, and conversation context.

Here is the database schema:

Table: locations
  - id: int
  - created_at: timestamp
  - name: text
  - lat: float8
  - lng: float8

Table: food_item
  - id: int
  - created_at: timestamp
  - name: text
  - description: text
  - gluten_free: boolean
  - vegan: boolean
  - vegetarian: boolean
  - kosher: boolean
  - type: enum("meat", "dairy", "produce", "grains", "prepared")
  - location_id: int (foreign key referencing locations.id)

- If the user wants to CREATE a new location and food items:
  1) Generate a unique, random positive 32-bit integer for the new location's 'id'. 
     Example: 123456789 or 2100000000 (1 <= id < 2147483648).
  2) Insert the new location with that 'id', 'created_at' (use CURRENT_TIMESTAMP or NOW()), 'name', 'lat', 'lng'.
  3) For each new food item mentioned:
     - Generate a unique int for food_item.id.
     - Insert into the 'food_item' table, referencing the same 'location_id' from step (1).
     - If the user provided dietary info (gluten_free, vegan, vegetarian, kosher, halal), set them as needed.
     - The 'description' and 'type' can be chosen or inferred from the user request. 
       If not stated, you can create a short placeholder.
  4) Output each statement in a single string, separated by semicolons, or on separate lines.
- Always ensure 'location_id' in food_item references the new location's 'id'.

### Important:
- If the user doesn't mention a specific column or filter, do not filter or set that column.
- Output only the SQL statements, with no additional commentary, code fences, or disclaimers.
"""
    user_prompt = f"""
User conversation (condensed/filtered):
{conversation}

Generate the final SQL query now.
"""
    response = openai.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        reasoning_effort="low",
    )
    sql_query = response.choices[0].message.content
    return sql_query.strip()


def fetch_db(sql_query: str) -> list:
    conn = psycopg2.connect(uri)
    results = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            results = cur.fetchall()
    finally:
        conn.close()
    return results


def main():
    # Example conversation snippet:
    # The user specifically asks for locations east of them, plus some dietary filters
    # conversation_history = """
    # User: My current location is lat=40.730610, lng=-73.935242.
    #       Can you return all the locations that are east of me?
    #       I only want places that serve vegan or vegetarian options.
    #       I'm okay with any food_item type.
    # """

    conversation_history = """
    User: My current location is lat=-89.999999, lng=-89.999999.
          Can you return all the locations that are near me?
          I only want places that have halal options.
          I'm okay with any food_item type.
    """

    # Generate the SQL query from the conversation
    sql_query = generate_sql_query(conversation_history)
    print("Generated SQL query:\n", sql_query)

    # Optionally, execute that query on the database
    results = fetch_db(sql_query)
    print("Query Results:\n", results)


if __name__ == "__main__":
    main()
