# ai/analysis/llm/openai_clients.py
from openai import OpenAI
import os

# ✅ 여기서만 모델 결정
DEFAULT_MODEL = "gpt-5.2"

_client = None


def get_client():
    """
    OpenAI client lazy initializer
    - API 키가 실제로 필요할 때만 검사
    """
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. "
                "Set it as an environment variable before running LLM analysis."
            )
        _client = OpenAI(api_key=api_key)

    return _client


def run_llm(
    *,
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 2048,
):
    """
    messages: [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ]
    """

    client = get_client()

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
        max_completion_tokens=max_tokens, 
    )

    return response.choices[0].message.content
