from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class BaseLLMClient:
    """Minimal client contract used by the orchestrator."""

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        timeout_sec: float = 60.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        raise NotImplementedError


@dataclass(slots=True)
class OpenAICompatClient(BaseLLMClient):
    """
    Minimal OpenAI-compatible Chat Completions client.
    - base_url may point to either the API root or the /v1 prefix
    - api_key is sent as a bearer token
    - model is passed through verbatim
    """

    base_url: str
    api_key: str
    model: str

    def _endpoint(self) -> str:
        url = self.base_url.rstrip("/")
        if not url.endswith("/v1"):
            url += "/v1"
        return url + "/chat/completions"

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        timeout_sec: float = 60.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }
        if extra:
            payload.update(extra)

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self._endpoint(),
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=float(timeout_sec)) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            obj = json.loads(raw)

            choices = obj.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                content = msg.get("content", "")
                if content:
                    return str(content)

                text = choices[0].get("text", "")
                if text:
                    return str(text)

            return ""

        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            raise RuntimeError(f"LLM HTTPError {e.code}: {body}") from e

        except urllib.error.URLError as e:
            raise RuntimeError(f"LLM URLError: {e}") from e

        except json.JSONDecodeError as e:
            raise RuntimeError(f"LLM JSONDecodeError: {e}") from e


@dataclass(slots=True)
class DummyLLMClient(BaseLLMClient):
    """
    Minimal dummy client for local debugging.
    - echo returns the last user message
    - fixed returns a constant string
    """

    mode: str = "echo"

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 256,
        timeout_sec: float = 1.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "") or ""
                break
        if self.mode == "fixed":
            return "OK"
        return last_user


def build_llm_client(
    *,
    dummy: bool = False,
    dummy_mode: str = "echo",
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseLLMClient:
    if dummy:
        return DummyLLMClient(mode=dummy_mode)

    b = (base_url or os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")).strip()
    k = (api_key or os.getenv("LLM_API_KEY", "sk-bbbf4830a5c54c6cac916c666c24027d")).strip()
    m = (model or os.getenv("LLM_MODEL", "deepseek-chat")).strip()

    if not (b and k and m):
        raise ValueError("Missing LLM config: need base_url/api_key/model (or env LLM_BASE_URL/LLM_API_KEY/LLM_MODEL).")

    return OpenAICompatClient(base_url=b, api_key=k, model=m)
