"""LLM query routing and response generation operations."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from google.api_core.exceptions import GoogleAPIError

from app.core.config import settings
from app.core.llm import llm_client
from app.core.security import verify_token
from app.models.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def submit_query(request: QueryRequest, current_user: str = Depends(verify_token)):
    """Processes a user's prompt via the LLM API.

    Requires an authenticated user via JWT dependency.

    Args:
        request: The QueryRequest containing the prompt text.
        current_user: Automatically injected validated user subject from token.

    Returns:
        A QueryResponse containing the AI generated content.

    Raises:
        HTTPException: Detailed exceptions for LLM timeouts, service errors, or validation issues.
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )

    try:
        # LLM execution wrapped in timeout to ensure the endpoint doesn't hang
        response_text = await asyncio.wait_for(
            llm_client.generate_response(request.query),
            timeout=settings.llm_timeout_seconds
        )
        return QueryResponse(response=response_text)
    
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM request timed out"
        )
    except GoogleAPIError as google_error:
        # In a real app, log google_error.message here
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider is currently unavailable or returned an error."
        )
    except Exception as generic_err:
        # In a real app, log generic_err here
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal server error occurred."
        )
