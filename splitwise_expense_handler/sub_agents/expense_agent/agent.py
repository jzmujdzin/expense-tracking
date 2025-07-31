from .prompt import expense_handling_agent_prompt, direct_expense_agent_prompt

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from splitwise import Splitwise

splitwise = Splitwise()

# group expense logic:
# group expense handler:
# lookup group on splitwise
# retrieve group members
# using itemized receipt ({receipt_items}), list of people involved (from user prompt), and user prompt,
# determine who consumed or is responsible for each item.
# If specific assignments are mentioned in the 'sharing_instructions' (user prompt), use them.
# Otherwise, suggest an equal split among 'assigned_people'.
# usually, 1 person pays for the expense and the rest owe them.
# then: create expense on splitwise


direct_expense_handler = Agent(name="direct_expense_handler",
                               model="gemini-2.0-flash",
    description="Direct expense handler",
    instruction=direct_expense_agent_prompt,
    tools=[splitwise.create_direct_expense_by_name]
)

group_expense_handler = Agent(name="group_expense_handler", model="gemini-2.0-flash", instruction="do nothing")

expense_handling_agent = Agent(
    name="expense_handling_agent",
    model="gemini-2.0-flash",
    description="Expense handling agent",
    instruction=expense_handling_agent_prompt,
    tools=[AgentTool(direct_expense_handler), AgentTool(group_expense_handler)],
)
