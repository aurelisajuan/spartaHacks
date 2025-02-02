# agent_swarm.py
from agents.triage_agent import TriageAgent
from agents.locator_agent import LocatorAgent, locator_instructions
from agents.supplier_agent import SupplierAgent, provider_instructions

from swarm import Swarm
from dotenv import load_dotenv
import os
from openai import OpenAI
from typing import Dict, List, Callable
import logging
from datetime import datetime


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize the Swarm client
client = Swarm()

# Initialize OpenAI client if needed
openai_client = OpenAI()

# Define the OpenAI model you're using
OPENAI_MODEL = "gpt-4o"  # Replace with your specific model if different


class AgentSwarm:
    def __init__(
        self,
        stream: bool = False,
        agent: bool = False,
    ):
        """
        Initialize the AgentSwarm with necessary agents and their corresponding functions.

        Args:
            socket: Handles real-time communication (e.g., sending messages).
        """

        # Initialize Agents with their instructions and functions, including the model
        self.triage_agent = TriageAgent(
            [
                self.transfer_to_locator,
                self.transfer_to_supplier,
            ]  # Add transfer function
        )

        self.locator_agent = LocatorAgent()

        self.supplier_agent = SupplierAgent()

        self.current_agent = self.triage_agent
        self.stream = stream

    # -------------------- Transfer Functions -------------------- #

    def transfer_to_locator(self, context_variables: Dict, user_message: str):
        """Transfers to the locator agent. Make sure to ask the user for their location and any dietary restrictions they may have after transferring to the locator agent.

        Args:
            context_variables (Dict): The context variables from the previous agent.
            user_message (str): The user's message.

        Returns:
            Dict: The response from the locator agent.
        """
        print("Context variables: ", context_variables)
        logging.info("Transferring to Locator Agent.")
        self.current_agent = self.locator_agent
        return {
            "value": "Transferring to Locator Agent. Ask the user for their location and any dietary restrictions they may have.",
            "agent": self.locator_agent,
        }

    def transfer_to_supplier(self, context_variables: Dict, user_message: str):
        """Transfers to the supplier agent. Make sure to ask the user the id of their supplier, or if it is a new supplier, ask for the supplier's name, address, and any other relevant information after transferring to the supplier agent.

        Args:
            context_variables (Dict): The context variables from the previous agent.
            user_message (str): The user's message.

        Returns:
            Dict: The response from the supplier agent.
        """
        logging.info("Transferring to Supplier Agent.")
        self.current_agent = self.supplier_agent
        return {
            "value": "Transferring to Supplier Agent. Ask the user the id of their supplier, or if it is a new supplier, ask for the supplier's name, address, and any other relevant information.",
            "agent": self.supplier_agent,
        }

    # -------------------- Run Function -------------------- #

    def run(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        context_variables: Dict = {},
    ):
        """
        Executes the swarm by running the Triage Agent with the provided messages.

        Args:
            messages (List[Dict[str, str]]): List of messages to process.
            stream (bool): Whether to stream the response.

        Yields:
            str: The assistant's response chunks.
        """

        # Run the swarm with the accumulated messages
        response = client.run(
            agent=self.current_agent,
            messages=messages,
            stream=stream,
        )

        return response
