from google.adk.agents import Agent

from .types import Receipt
from .prompt import intent_agent_prompt
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from loguru import logger
import expense_agent

root_agent = Agent(
    name="user_intent_agent",
    model="gemini-2.0-flash",
    instruction=intent_agent_prompt,
    tools=[expense_agent]
)
