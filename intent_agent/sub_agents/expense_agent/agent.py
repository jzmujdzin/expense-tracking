from ..receipt_agent import receipt_itemization_agent
from .prompt import expense_handling_agent_prompt, direct_expense_agent_prompt

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from splitwise import Splitwise

splitwise = Splitwise()

# lookup group on splitwise
# retrieve group members
# using itemized receipt, list of people involved, and user prompt, [SAVE RECEIPT FROM FIRST AGENT]
# determine who consumed or is responsible for each item.
# If specific assignments are mentioned in the 'sharing_instructions', use them. [SAVE THEM FROM INITIAL AGENT]
# Otherwise, suggest an equal split among 'assigned_people'.

# retrieve itemized receipt

# then: check whether the expense is direct or group expense
# if group expense, lookup group on splitwise. retrieve group members.

# using itemized receipt, list of people involved, and user prompt,
# determine who consumed or is responsible for each item.
# If specific assignments are mentioned in the 'sharing_instructions', use them.
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

expense_agent = SequentialAgent(name="receipt_to_expense_handler",
                                sub_agents=[
    receipt_itemization_agent,
    # expense_handling_agent
])