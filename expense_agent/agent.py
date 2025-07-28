from google.adk.agents import Agent

from .types import Receipt
from .prompt import receipt_itemization_agent_prompt
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from loguru import logger

# lookup group on splitwise
# retrieve group members



root_agent = Agent(
    name="receipt_itemization_agent",
    model="gemini-2.0-flash",
    description="Receipt itemization agent",
    instruction=receipt_itemization_agent_prompt,
    output_schema=Receipt,
)
