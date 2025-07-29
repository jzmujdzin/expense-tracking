from google.adk.agents import Agent

from .prompt import intent_agent_prompt
import expense_agent

root_agent = Agent(
    name="user_intent_agent",
    model="gemini-2.0-flash",
    instruction=intent_agent_prompt,
    tools=[expense_agent]
)
