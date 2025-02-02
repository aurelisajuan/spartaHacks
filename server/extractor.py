from pydantic import BaseModel
from typing import Literal
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

from util import get_geocode


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


class SupplierDetails(BaseModel):
    name: str
    phone_number: str
    address: str
    supplier_id: int
    food_items: list[FoodItem]


extract_food_items_prompt = """You are an expert at extracting food items from a transcript of a conversation.

Here is the transcript:
{text}

Extract the food items from the transcript. Analyze weather each individual item is gluten-free, vegan, vegetarian, halal, or kosher.
If Supplier details is present, extract the supplier details. Else just return empty strings and -1 for the supplier_id.
"""


def extract_food_items(text: str) -> FoodItemList:
    completion = client.beta.chat.completions.parse(
        model="o3-mini",
        reasoning_effort="low",
        messages=[
            {"role": "user", "content": extract_food_items_prompt.format(text=text)}
        ],
        response_format=SupplierDetails,
    )

    supplier_details = completion.choices[0].message.parse

    if supplier_details.address:
        supplier_details.address = get_geocode(supplier_details.address)

    return supplier_details


# Supplier only
def process_transcript(transcript: str) -> FoodItemList:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "extract_food_items",
                "description": "Extract food items from a transcript of a conversation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                    },
                    "required": ["text"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]

    prompt = """Analyze the provided transcript. If the transcript is a supplier calling in with excess food items, call the extract_food_items function. 
    Do not call the function if the transcript is a locator calling in to find a location to get food items.
    
    The transcript is:
    {transcript}
    
    Output a json object with the following fields:
    "title": "A title for the conversation" | string
    "food_items": "The food items extracted from the transcript" | string | eg. "carrots, lettuce, and tomatoes" or ""
    """
    print("Transcript: " + prompt.format(transcript=transcript))
    messages = [{"role": "user", "content": prompt.format(transcript=transcript)}]
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        response_format={"type": "json_object"},
    )

    if completion.choices[0].message.tool_calls:
        tool_call = completion.choices[0].message.tool_calls[0]
        extracted_items = extract_food_items(transcript)
        messages.append(completion.choices[0].message)
        messages.append(
            {
                "role": "tool",
                "content": "Completed the tool call successfully",
                "tool_call_id": tool_call.id,
            }
        )

        completion2 = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return completion2.choices[0].message.content
    else:
        return completion.choices[0].message.content


if __name__ == "__main__":
    dummy_supplier_call = """
    Hi, I'm from Second Harvest Food Bank and we have some extra food items to contribute today.
    
    We have about 50 pounds of fresh produce including carrots, lettuce, and tomatoes. 
    
    We also have 30 loaves of whole wheat bread that are gluten-free.
    
    And we have some prepared meals - about 25 vegetarian lasagnas that are also gluten-free.
    
    Finally, we have 20 gallons of milk and 15 pounds of cheese.
    """
    results = process_transcript(dummy_supplier_call)
    print(results)

    dummy_locator_call = """
    Hi, I'm from the Red Cross and we need to find a location to donate food items to.
    """
    results = process_transcript(dummy_locator_call)
    print(results)
