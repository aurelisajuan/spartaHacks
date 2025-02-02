from pydantic import BaseModel
from typing import Literal
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


class FoodItem(BaseModel):
    name: str
    description: str
    type: Literal["meat", "dairy", "produce", "grains", "prepared"]
    gluten_free: bool
    vegan: bool
    vegetarian: bool
    halal: bool
    kosher: bool


class FoodItemList(BaseModel):
    items: list[FoodItem]


prompt = """You are an expert at extracting food items from a transcript of a conversation.

Here is the transcript:
{text}

Extract the food items from the transcript. Analyze weather each individual item is gluten-free, vegan, vegetarian, halal, or kosher.
"""


def extract_food_items(text: str) -> FoodItemList:
    completion = client.beta.chat.completions.parse(
        model="o3-mini",
        reasoning_effort="low",
        messages=[{"role": "user", "content": prompt.format(text=text)}],
        response_format=FoodItemList,
    )

    items = completion.choices[0].message.parsed
    return items


if __name__ == "__main__":
    dummy_conversation = """
    Hi, I'm from Second Harvest Food Bank and we have some extra food items to contribute today.
    
    We have about 50 pounds of fresh produce including carrots, lettuce, and tomatoes. 
    
    We also have 30 loaves of whole wheat bread that are gluten-free.
    
    And we have some prepared meals - about 25 vegetarian lasagnas that are also gluten-free.
    
    Finally, we have 20 gallons of milk and 15 pounds of cheese.
    """
    items = extract_food_items(dummy_conversation)
    print(items)
