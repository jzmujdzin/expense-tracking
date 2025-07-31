from google.adk.agents import SequentialAgent

from .sub_agents.expense_agent import expense_handling_agent
from .sub_agents.receipt_agent import receipt_itemization_agent


root_agent = SequentialAgent(name="receipt_to_expense_handler",
                                sub_agents=[
    receipt_itemization_agent,
    expense_handling_agent
])