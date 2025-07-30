from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool


from .prompt import intent_agent_prompt
from .sub_agents.expense_agent import expense_agent


root_agent = Agent(
    name="user_intent_agent",
    model="gemini-2.0-flash",
    instruction=intent_agent_prompt,
    tools=[AgentTool(expense_agent)]
)
