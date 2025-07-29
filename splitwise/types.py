from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Self, Any
from loguru import logger

# add enum for POST/GET methods
class RequestMethod(str):
    """
    Enum for HTTP request methods.
    """
    GET = "GET"
    POST = "POST"

class SplitwiseApiPaths(str):
    """
    Enum for Splitwise API paths.
    """
    GET_CURRENT_USER = "/get_current_user"
    GET_FRIENDS = "/get_friends"
    GET_GROUPS = "/get_groups"
    GET_GROUP = "/get_group/{group_id}"
    CREATE_EXPENSE = "/create_expense"

class SplitwiseMember(BaseModel):
    """
    Represents a person in the Splitwise system.
    """
    id: int
    first_name: str
    last_name: str | None = None

class SplitwiseGroup(BaseModel):
    """
    Represents a group in the Splitwise system.
    """
    id: int
    name: str
    members: list[SplitwiseMember]

class SplitwiseExpenseParticipant(BaseModel):
    """
    Represents a participant in a Splitwise expense, detailing their share.
    Aligns with the 'users' array in the Splitwise API payload.
    """
    user_id: int = Field(..., description="The ID of the user participating in the expense.")
    paid_share: float = Field(..., description="The amount this user paid for the expense.")
    owed_share: Optional[float] = Field(0.0, description="The amount this user owes for the expense. Required for 'by_shares' split, can be omitted for 'equal_group_split'.")

    @model_validator(mode='after')
    def round_shares(self) -> 'SplitwiseExpenseParticipant':
        """Ensure shares are rounded to two decimal places."""
        self.paid_share = round(self.paid_share, 2)
        if self.owed_share is not None:
            self.owed_share = round(self.owed_share, 2)
        return self

class SplitwiseExpense(BaseModel):
    cost: float = Field(..., description="The total cost of the expense.")
    description: str = Field(..., description="A brief description of the expense.")
    currency_code: str = Field(..., description="The currency code (e.g., 'USD', 'PLN').")
    group_id: Optional[int] = Field(0, description="ID of the group the expense belongs to. If omitted, expense is direct.")
    participants: Optional[List[SplitwiseExpenseParticipant]] = Field(None, description="A list of participants and their paid/owed shares. Required if not using split_equally or for custom splits.")
    split_equally: Optional[bool] = Field(False,
                                          description="If True, the expense will be split equally among all members of the specified group.")

    @model_validator(mode='after')
    def validate_shares_and_split_type(self) -> Self:
        """
        Performs validation checks for shares and split type consistency.
        """
        total_paid = sum(p.paid_share for p in self.participants)
        if total_paid != self.cost:
            # add this to the first user's owed share
            self.participants[0].paid_share += self.cost - total_paid
            logger.info("Adjusted paid share for first participant to match total cost.")
        total_owed = sum(p.owed_share for p in self.participants)
        if total_owed != self.cost:
            self.participants[0].owed_share += self.cost - total_owed
            logger.info("Adjusted owed share for first participant to match total cost.")
        # --- Basic Validation ---
        if self.cost <= 0:
            raise ValueError("Expense cost must be positive.")
        if not self.description.strip():
            raise ValueError("Expense description cannot be empty.")
        if not self.currency_code.strip():
            raise ValueError("Currency code cannot be empty.")


    def to_api_payload(self) -> dict[str, Any]:
        """
        Converts the Pydantic model instance into the flattened dictionary
        format required by the Splitwise API's /create_expense endpoint.
        """
        payload = dict()

        # Required fields
        payload = self.dict(include={"description", "currency_code"})
        payload["cost"] = f"{self.cost:.2f}"
        # Handle 'split_equally' boolean conversion
        if self.split_equally:
            payload["split_equally"] = str(self.split_equally).lower()

        # Flatten 'users' (participants) list for the API payload
        if self.participants:
            for i, participant in enumerate(self.participants):
                payload[f"users__{i}__user_id"] = participant.user_id
                payload[f"users__{i}__paid_share"] = f"{participant.paid_share:.2f}"
                payload[f"users__{i}__owed_share"] = f"{participant.owed_share:.2f}"

        return payload