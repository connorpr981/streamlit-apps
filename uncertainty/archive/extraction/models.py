from pydantic import BaseModel, Field
from enum import Enum

class BeliefType(Enum):
    EMPIRICAL = "empirical"
    RATIONAL = "rational"
    AXIOLOGICAL = "axiological"
    METAPHYSICAL = "metaphysical"
    OTHER = "other"

class Belief(BaseModel):
    belief: str
    type: BeliefType = Field(
        description="Correctly assign one of the predefined belief types to the belief."
    )
    context: str
    justification: str
    confidence: str


    

class UserDetail(BaseModel):
    age: int
    name: str
    role: Role = Field(
        description="Correctly assign one of the predefined roles to the user."
    )

