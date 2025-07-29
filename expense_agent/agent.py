from google.adk.agents import Agent

from .prompt import receipt_itemization_agent_prompt


# lookup group on splitwise
# retrieve group members
# using itemized receipt, list of people involved, and user prompt,
# determine who consumed or is responsible for each item.
# If specific assignments are mentioned in the 'sharing_instructions', use them.
# Otherwise, suggest an equal split among 'assigned_people'.



root_agent = Agent(
    name="receipt_itemization_agent",
    model="gemini-2.0-flash",
    description="Receipt itemization agent",
    instruction=receipt_itemization_agent_prompt,
)
