from pydantic import BaseModel

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

