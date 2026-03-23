from __future__ import annotations

from typing import AsyncGenerator, List, Optional

import httpx
from openai import OpenAI, OpenAIError

from config import get_settings
from models.schemas import ChatMessage


settings = get_settings()


def _build_client() -> OpenAI:
    """
    Use Groq if GROQ_API_KEY is set (free, works immediately).
    Otherwise use Hugging Face (requires enabling a model in HF settings).
    """
    if settings.GROQ_API_KEY:
        http_client = httpx.Client(
            base_url="https://api.groq.com/openai/v1",
            follow_redirects=True,
            timeout=30.0,
        )
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
            http_client=http_client,
        )
    if not settings.HF_TOKEN:
        raise RuntimeError(
            "Set GROQ_API_KEY in .env (get free key at https://console.groq.com) "
            "OR set HF_TOKEN and enable a model at https://huggingface.co/settings/inference-providers"
        )
    http_client = httpx.Client(
        base_url=settings.HF_BASE_URL,
        follow_redirects=True,
        timeout=30.0,
    )
    return OpenAI(
        base_url=settings.HF_BASE_URL,
        api_key=settings.HF_TOKEN,
        http_client=http_client,
    )


def _get_model() -> str:
    """Return the model name for the active provider."""
    return settings.GROQ_MODEL if settings.GROQ_API_KEY else settings.HF_MODEL


client = _build_client()


def build_chat_messages(
    user_message: str,
    history: List[ChatMessage],
) -> List[dict]:
    """
    Build the messages payload for the chat completion, including the system prompt.
    """
    messages: List[dict] = [
        {"role": "system", "content": settings.SYSTEM_PROMPT},
    ]

    for msg in history:
        # Ensure only valid roles are passed through; default to "user" if unknown
        role = msg.role if msg.role in {"system", "user", "assistant"} else "user"
        messages.append({"role": role, "content": msg.content})

    messages.append({"role": "user", "content": user_message})
    return messages


async def stream_chat_completion(
    user_message: str,
    history: List[ChatMessage],
    *,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """
    Call the LLM and stream the response text chunks.
    """
    messages = build_chat_messages(user_message, history)

    # Normalize parameters with safe defaults and caps from settings
    temp = (
        float(temperature)
        if temperature is not None
        else settings.DEFAULT_TEMPERATURE
    )
    temp = max(settings.MIN_TEMPERATURE, min(settings.MAX_TEMPERATURE, temp))

    mt = (
        int(max_tokens)
        if max_tokens is not None
        else settings.DEFAULT_MAX_TOKENS
    )
    mt = max(settings.MIN_MAX_TOKENS, min(settings.MAX_MAX_TOKENS, mt))

    try:
        response = client.chat.completions.create(
            model=_get_model(),
            messages=messages,
            temperature=temp,
            max_tokens=mt,
            stream=True,
        )

        for chunk in response:
            # Each chunk.choices[0].delta.content may be None or a string fragment
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and getattr(delta, "content", None):
                yield delta.content

    except OpenAIError as exc:
        msg = str(exc)
        if "500" in msg or "Internal server error" in msg:
            msg = (
                "Hugging Face API returned a server error (500). "
                "Try in .env: HF_MODEL=Qwen/Qwen2.5-7B-Instruct-1M:fastest "
                "or add :fastest to your current model (e.g. model:fastest)."
            )
        raise RuntimeError(msg) from exc
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected error while calling LLM: {exc}") from exc

