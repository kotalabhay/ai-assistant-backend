"""Pydantic schemas for request and response validation."""

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Request model for user login.

    Attributes:
        username: The user's account name.
        password: The user's secret password.
    """
    
    username: str = Field(..., description="The user's username")
    password: str = Field(..., description="The user's password")


class LoginResponse(BaseModel):
    """Response model for successful login.

    Attributes:
        access_token: The generated JWT.
        token_type: The type of token (e.g., bearer).
    """

    access_token: str
    token_type: str = "bearer"


class QueryRequest(BaseModel):
    """Request model for submitting a query.

    Attributes:
        query: The string input to be processed by the LLM.
    """

    query: str = Field(..., max_length=4000, description="The text query to send to the LLM")

    @field_validator('query')
    @classmethod
    def trim_query(cls, v: str) -> str:
        """Trims whitespace from the query string."""
        return v.strip()


class QueryResponse(BaseModel):
    """Response model containing the LLM output.

    Attributes:
        response: The generated response text.
    """

    response: str
