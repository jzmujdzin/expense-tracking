from google.adk.agents import Agent

from .types import Receipt
from .prompts import receipt_itemization_agent_prompt

root_agent = Agent(
    name="receipt_itemization_agent",
    model="gemini-2.0-flash",
    description="Receipt itemization agent",
    instruction=receipt_itemization_agent_prompt,
    output_schema=Receipt,
)
