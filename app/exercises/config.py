"""
Shared provider configuration for all exercises.
Each exercise calls make_headers() / get_endpoint() at request time,
so the user can change provider/model/key without restarting.
"""

# ── Provider registry ────────────────────────────────────────────────────────
# Each entry: id, label, base_url, chat_path, models_path, header_builder,
#             models list (populated by fetch or hardcoded fallback),
#             default_model

PROVIDERS = {
    "anthropic": {
        "label":       "Anthropic",
        "base_url":    "http://localhost:6655/anthropic/v1",
        "chat_path":   "/messages",
        "models_path": "/models",
        "models": [
            "claude-sonnet-4-6",
            "claude-opus-4-7",
            "claude-haiku-4-5-20251001",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ],
    },
    "openai": {
        "label":       "OpenAI",
        "base_url":    "http://localhost:6655/openai/v1",
        "chat_path":   "/chat/completions",
        "models_path": "/models",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
    },
    "gemini": {
        "label":       "Gemini",
        "base_url":    "http://localhost:6655/gemini",
        "chat_path":   None,   # dynamic: /v1beta/models/{model}:generateContent
        "models_path": "/v1beta/models",
        "models": [
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
    },
    "litellm": {
        "label":       "LiteLLM",
        "base_url":    "http://localhost:6655/litellm/v1",
        "chat_path":   "/chat/completions",
        "models_path": "/models",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-sonnet-4-6",
            "gemini-2.0-flash",
        ],
    },
}

PROVIDER_LABELS = [v["label"] for v in PROVIDERS.values()]
PROVIDER_IDS    = list(PROVIDERS.keys())

DEFAULT_PROVIDER = "anthropic"


def label_to_id(label: str) -> str:
    for pid, pdata in PROVIDERS.items():
        if pdata["label"] == label:
            return pid
    return DEFAULT_PROVIDER


def get_models(provider_id: str) -> list:
    return PROVIDERS[provider_id]["models"]


def get_default_model(provider_id: str) -> str:
    return PROVIDERS[provider_id]["models"][0]


def make_headers(provider_id: str, api_key: str) -> dict:
    """Return the correct headers for the given provider."""
    base = {"content-type": "application/json"}
    if provider_id == "anthropic":
        base["x-api-key"] = api_key
        base["anthropic-version"] = "2023-06-01"
    else:
        # OpenAI-compatible (OpenAI, LiteLLM, Gemini via proxy)
        base["Authorization"] = f"Bearer {api_key}"
    return base


def get_chat_url(provider_id: str, model: str) -> str:
    """Return the full chat endpoint URL."""
    p = PROVIDERS[provider_id]
    if provider_id == "gemini":
        return f"{p['base_url']}/v1beta/models/{model}:generateContent"
    return p["base_url"] + p["chat_path"]


def build_payload(provider_id: str, model: str, messages: list,
                  max_tokens: int = 1024, system: str = None,
                  tools: list = None, stream: bool = False) -> dict:
    """
    Build the request payload in the format each provider expects.
    Anthropic uses 'system' at top-level + 'messages' without system role.
    OpenAI/LiteLLM/Gemini use a system message inside the messages array.
    """
    if provider_id == "anthropic":
        payload = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = tools
        if stream:
            payload["stream"] = True
    elif provider_id == "gemini":
        # Gemini uses 'contents' with 'parts'
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        payload = {"contents": contents}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
    else:
        # OpenAI-compatible
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.extend(messages)
        payload = {"model": model, "max_tokens": max_tokens, "messages": msgs}
        if tools:
            payload["tools"] = tools
        if stream:
            payload["stream"] = True
    return payload


def parse_reply(provider_id: str, data: dict) -> str:
    """Extract the assistant text from a non-streaming response."""
    if provider_id == "anthropic":
        return data["content"][0]["text"]
    elif provider_id == "gemini":
        return data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return data["choices"][0]["message"]["content"]
