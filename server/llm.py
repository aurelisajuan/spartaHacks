from dotenv import load_dotenv

load_dotenv()
from openai import AsyncOpenAI
from typing import List, Dict, Any
import os
from custom_types import (
    ResponseRequiredRequest,
    ResponseResponse,
    Utterance,
    ToolCallInvocationResponse,
    ToolCallResultResponse,
    AgentInterruptResponse,
)
from functions import convert_address_to_coords, query_db
from prompts import locator_instructions, provider_instructions, triage_instructions
import json


class LlmClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.mode = "triage"

    def draft_begin_message(self):
        response = ResponseResponse(
            response_id=0,
            content="Welcome to FoodLink! Are you looking to find food in your area, or are you a provider wanting to contribute food?",
            content_complete=True,
            end_call=False,
        )
        return response

    def convert_transcript_to_openai_messages(self, transcript: List[Utterance]):
        messages = []
        for utterance in transcript:
            if utterance.role == "agent":
                messages.append({"role": "assistant", "content": utterance.content})
            else:
                messages.append({"role": "user", "content": utterance.content})
        return messages

    def prepare_prompt(self, request: ResponseRequiredRequest):
        prompt = [
            {
                "role": "system",
                "content": (
                    triage_instructions
                    if self.mode == "triage"
                    else (
                        provider_instructions
                        if self.mode == "provider"
                        else locator_instructions
                    )
                ),
            }
        ]
        transcript_messages = self.convert_transcript_to_openai_messages(
            request.transcript
        )
        for message in transcript_messages:
            prompt.append(message)

        if request.interaction_type == "reminder_required":
            prompt.append(
                {
                    "role": "user",
                    "content": "(Now the user has not responded in a while, you would say:)",
                }
            )
        return prompt

    def prepare_functions(self) -> List[Dict[str, Any]]:
        """
        Define the available function calls for the assistant.
        """
        end_call_function = {
            "type": "function",
            "function": {
                "name": "end_call",
                "description": "End the call when user says goodbye",
                "parameters": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                },
            },
        }
        if self.mode == "triage":
            return [
                {
                    "type": "function",
                    "function": {
                        "name": "transfer",
                        "description": "Transfer's call to designated agent. You must call the function with arguments. Allowed agents: 'locator', 'provider'",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "agent": {"type": "string"},
                            },
                            "required": ["agent"],
                        },
                    },
                },
            ] + [end_call_function]
        elif self.mode == "provider":
            return [end_call_function]
        elif self.mode == "locator":
            return [
                {
                    "type": "function",
                    "function": {
                        "name": "convert_address_to_coords",
                        "description": "Convert an address to geographic coordinates.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "address": {
                                    "type": "string",
                                    "description": "The address to convert.",
                                },
                                "message": {
                                    "type": "string",
                                    "description": "The message to be said while converting the address to coordinates.",
                                },
                            },
                            "required": ["address", "message"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "query_db",
                        "description": "Query the database for locator information based on provided parameters.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Summarize what the user is looking for: eg. Meat near coords (lat, lng) that is kosher.",
                                },
                                "message": {
                                    "type": "string",
                                    "description": "The message to be said while querying the database.",
                                },
                            },
                            "required": ["query", "message"],
                        },
                    },
                },
            ] + [end_call_function]

    async def draft_response(self, request: ResponseRequiredRequest):
        # Initialize conversation with the user prompt.
        conversation = self.prepare_prompt(request)
        response_id = request.response_id

        # Loop until no new tool calls are generated.
        while True:
            func_calls = {}
            stream = await self.client.chat.completions.create(
                model="gpt-4o",  # Or use a 3.5 model for speed.
                messages=conversation,
                stream=True,
                tools=self.prepare_functions(),
            )
            tool_calls = False
            # Process streaming response.
            async for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # Accumulate function call parts.
                if delta.tool_calls:
                    tool_calls = True
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in func_calls:
                            func_calls[idx] = tc
                        else:
                            func_calls[idx].function.arguments += (
                                tc.function.arguments or ""
                            )

                # Yield any text content.
                if delta.content and not tool_calls:
                    print("Yielding:", delta.content)
                    yield ResponseResponse(
                        response_id=response_id,
                        content=delta.content,
                        content_complete=False,
                        end_call=False,
                    )

            print("Accumulated function calls:", func_calls)

            # If no tool calls were made, we're done.
            if not func_calls:
                break

            # Process each tool call (handle multiple calls if present).
            new_messages = []
            for idx in sorted(func_calls.keys()):
                fc = func_calls[idx]

                # Append the assistant message that originally triggered the function call.
                new_messages.append(
                    {"role": "assistant", "tool_calls": [fc], "content": ""}
                )

                try:
                    args = json.loads(fc.function.arguments)
                except Exception:
                    args = {}

                print("Processing function call:", fc.function.name)
                yield ToolCallInvocationResponse(
                    tool_call_id=fc.id,
                    name=fc.function.name,
                    arguments=fc.function.arguments,
                )

                # Process the function call and append a tool response.
                if fc.function.name == "end_call":
                    yield ResponseResponse(
                        response_id=response_id,
                        content=args.get("message", ""),
                        content_complete=True,
                        end_call=True,
                    )
                    yield ToolCallResultResponse(
                        tool_call_id=fc.id,
                        content=args.get("message", ""),
                    )
                    return
                elif fc.function.name == "transfer":
                    self.mode = args.get("agent")

                    new_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": fc.id,
                            "content": f"Transferred call to {args.get('agent')}",
                        }
                    )
                    yield ToolCallResultResponse(
                        tool_call_id=fc.id,
                        content=f"Transferred call to {args.get('agent')}",
                    )
                elif fc.function.name == "convert_address_to_coords":
                    address = args.get("address")
                    yield ResponseResponse(
                        response_id=response_id,
                        content=args.get("message", ""),
                        content_complete=False,
                        end_call=False,
                    )

                    output = convert_address_to_coords(address)
                    print("Converted address output:", output)
                    new_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": fc.id,
                            "content": output,
                        }
                    )
                    yield ToolCallResultResponse(
                        tool_call_id=fc.id,
                        content=output,
                    )
                elif fc.function.name == "query_db":
                    yield ResponseResponse(
                        response_id=response_id,
                        content=args.get("message", ""),
                        content_complete=False,
                        end_call=False,
                    )
                    # Optionally yield an intermediate response.
                    query = args.get("query", "")
                    output = query_db(query)
                    print("Database query output:", output)
                    new_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": fc.id,
                            "content": output,
                        }
                    )
                # Additional functions can be added here.

            # Extend the conversation with the tool call responses.
            conversation.extend(new_messages)

        # After all rounds, yield a final complete response.
        yield ResponseResponse(
            response_id=response_id,
            content="",
            content_complete=True,
            end_call=False,
        )
