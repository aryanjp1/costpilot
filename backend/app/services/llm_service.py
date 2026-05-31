import logging

from ..config import get_settings

logger = logging.getLogger("costpilot.llm")
settings = get_settings()


async def summarize_recommendations(context: str) -> str | None:
    """Optionally use an LLM to write a natural-language savings summary.

    Falls back to None when no API key is configured, so the recommendation
    endpoint always works offline.
    """
    if not settings.openai_api_key:
        return None
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a FinOps assistant for LLM spending. "
                    "Summarize the optimization opportunities in two sentences.",
                },
                {"role": "user", "content": context},
            ],
            max_tokens=160,
        )
        return response.choices[0].message.content
    except Exception:
        logger.exception("LLM summary failed")
        return None
