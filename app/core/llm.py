"""Google Gemini API wrapper for processing LLM queries."""

import asyncio

import google.generativeai as genai

from app.core.config import settings


class LLMClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self) -> None:
        """Initializes the Gemini client with the API key from settings."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-flash-latest")

    async def generate_response(self, text: str) -> str:
        """Generates a response from the Gemini model given a text query.

        Args:
            text: The user's input query.

        Returns:
            The generated response text.
            
        Raises:
            Exception: If there's an API error from Gemini or it times out.
        """
        # Run synchronous call in threadpool since Gemini Python SDK generates async issues
        # Or using native async generation:
        response = await self.model.generate_content_async(text)
        return response.text


# Singleton client instance
llm_client = LLMClient()
