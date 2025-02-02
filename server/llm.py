from dotenv import load_dotenv

load_dotenv()
from openai import AsyncOpenAI
from typing import List
import os
from custom_types import (
    ResponseRequiredRequest,
    ResponseResponse,
    Utterance,
)
from agent_swarm import AgentSwarm


class LlmClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.agent_swarm = AgentSwarm()

    def draft_begin_message(self):
        response = ResponseResponse(
            response_id=0,
            content="Welcome to FoodLink! Are you looking to find food in your area, or are you a supplier wanting to contribute food?",
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
        prompt = []
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

    async def draft_response(self, request: ResponseRequiredRequest):
        prompt = self.prepare_prompt(request)
        stream = self.agent_swarm.run(prompt, stream=True, context_variables={"messages": prompt})

        print(stream)
        for chunk in stream:
            if "content" in chunk and chunk["content"]:
                response = ResponseResponse(
                    response_id=request.response_id,
                    content=chunk["content"],
                    content_complete=False,
                    end_call=False,
                )
                yield response

        # Send final response with "content_complete" set to True to signal completion
        response = ResponseResponse(
            response_id=request.response_id,
            content="",
            content_complete=True,
            end_call=False,
        )
        yield response
