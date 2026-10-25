"""AI provider abstraction. API keys stay on the server and are never logged or returned."""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import requests

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class ProviderError(Exception):
    """kind: unconfigured | blocked | timeout | rate_limit | auth | unavailable | http | bad_response"""

    def __init__(self, kind: str, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.kind, self.message, self.retry_after = kind, message, retry_after


@dataclass
class ProviderResult:
    text: str
    model: str
    usage: dict = field(default_factory=dict)


class BaseProvider:
    name = "none"
    supports_vision = False

    def __init__(self, cfg: dict):
        self.model = cfg.get("AI_MODEL", "")
        self.base_url = (cfg.get("AI_BASE_URL") or "").rstrip("/")
        self.key = cfg.get("AI_API_KEY", "")

    @property
    def is_external(self) -> bool:
        host = (urlsplit(self.base_url).hostname or "").lower() if self.base_url else ""
        return host not in LOCAL_HOSTS

    def describe(self) -> dict:
        return {"provider": self.name, "model": self.model, "external": self.is_external, "vision_capable": self.supports_vision}

    def generate(self, system: str, messages: list[dict], max_tokens: int, timeout: int, images: list[tuple[str, bytes]] | None = None) -> ProviderResult:
        raise NotImplementedError

    @staticmethod
    def _raise_for(resp: requests.Response):
        if resp.status_code in (401, 403):
            raise ProviderError("auth", "The AI provider rejected the server's credentials.")
        if resp.status_code == 429:
            ra = resp.headers.get("Retry-After", "")
            raise ProviderError("rate_limit", "The AI provider is rate-limiting requests. Try again shortly.", int(ra) if ra.isdigit() else None)
        if resp.status_code >= 500:
            raise ProviderError("unavailable", f"The AI provider is temporarily unavailable (HTTP {resp.status_code}).")
        if resp.status_code >= 400:
            raise ProviderError("http", f"The AI provider returned an error (HTTP {resp.status_code}).")

    def _post(self, url, headers, body, timeout):
        try:
            return requests.post(url, headers=headers, json=body, timeout=(5, timeout))
        except requests.Timeout:
            raise ProviderError("timeout", "The AI provider did not respond in time.")
        except requests.ConnectionError:
            raise ProviderError("unavailable", "Could not reach the AI provider.")
        except requests.RequestException:
            raise ProviderError("unavailable", "The AI request failed.")


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    supports_vision = True

    def __init__(self, cfg):
        super().__init__(cfg)
        self.base_url = self.base_url or "https://api.anthropic.com"

    def generate(self, system, messages, max_tokens, timeout, images=None):
        msgs = [dict(m) for m in messages]
        if images and msgs and msgs[-1]["role"] == "user":
            blocks = [{"type": "image", "source": {"type": "base64", "media_type": mime, "data": base64.b64encode(data).decode()}} for mime, data in images]
            blocks.append({"type": "text", "text": msgs[-1]["content"]})
            msgs[-1] = {"role": "user", "content": blocks}
        r = self._post(f"{self.base_url}/v1/messages", {"x-api-key": self.key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                       {"model": self.model, "max_tokens": max_tokens, "system": system, "messages": msgs, "temperature": 0}, timeout)
        self._raise_for(r)
        try:
            j = r.json()
            text = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
            return ProviderResult(text.strip(), j.get("model", self.model), j.get("usage", {}))
        except Exception:
            raise ProviderError("bad_response", "The AI provider returned an unreadable response.")


class OpenAICompatProvider(BaseProvider):
    """OpenAI, Azure-style gateways, or a local server (Ollama, vLLM, LM Studio) via /chat/completions."""
    name = "openai_compatible"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.base_url = self.base_url or "https://api.openai.com/v1"

    def generate(self, system, messages, max_tokens, timeout, images=None):
        if images:
            raise ProviderError("http", "This provider is not configured for image input.")
        headers = {"content-type": "application/json"}
        if self.key:
            headers["authorization"] = f"Bearer {self.key}"
        r = self._post(f"{self.base_url}/chat/completions", headers,
                       {"model": self.model, "messages": [{"role": "system", "content": system}] + messages, "max_tokens": max_tokens, "temperature": 0}, timeout)
        self._raise_for(r)
        try:
            j = r.json()
            return ProviderResult((j["choices"][0]["message"]["content"] or "").strip(), j.get("model", self.model), j.get("usage", {}))
        except Exception:
            raise ProviderError("bad_response", "The AI provider returned an unreadable response.")


class MockProvider(BaseProvider):
    """TEST ONLY. Selected via AI_PROVIDER=mock and honoured only when the app runs with TESTING=True."""
    name = "mock"
    responder = None  # callable(system, messages, images) -> str | raises ProviderError
    calls: list = []

    def __init__(self, cfg):
        super().__init__(cfg)
        self.model = "mock-test-model"
        self.base_url = "http://127.0.0.1"

    def generate(self, system, messages, max_tokens, timeout, images=None):
        MockProvider.calls.append({"system": system, "messages": messages, "images": images})
        if MockProvider.responder:
            return ProviderResult(MockProvider.responder(system, messages, images), self.model)
        raise ProviderError("unavailable", "mock provider has no responder")


def get_provider(cfg: dict) -> BaseProvider:
    """Return a configured provider or raise ProviderError('unconfigured')."""
    name = (cfg.get("AI_PROVIDER") or "").lower()
    if not name:
        raise ProviderError("unconfigured", "No AI provider is configured (AI_PROVIDER is empty).")
    if name == "mock":
        if not cfg.get("TESTING"):
            raise ProviderError("unconfigured", "The mock provider is only available in automated tests.")
        return MockProvider(cfg)
    if not cfg.get("AI_MODEL"):
        raise ProviderError("unconfigured", "AI_MODEL is not set.")
    if name == "anthropic":
        if not cfg.get("AI_API_KEY"):
            raise ProviderError("unconfigured", "AI_API_KEY is not set.")
        return AnthropicProvider(cfg)
    if name in ("openai", "openai_compatible", "local"):
        p = OpenAICompatProvider(cfg)
        if p.is_external and not cfg.get("AI_API_KEY"):
            raise ProviderError("unconfigured", "AI_API_KEY is not set.")
        return p
    raise ProviderError("unconfigured", f"Unknown AI_PROVIDER '{name[:30]}'. Use anthropic, openai_compatible or local.")


def check_phi_allowed(cfg: dict, provider: BaseProvider):
    if provider.is_external and not cfg.get("AI_ALLOW_EXTERNAL_PHI"):
        raise ProviderError("blocked", "Protected patient data cannot be sent to an external AI service until an administrator confirms an approved agreement (AI_ALLOW_EXTERNAL_PHI=1). Use a local model or complete that review.")
