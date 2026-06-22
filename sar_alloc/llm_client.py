from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .demo_policy import (
    demo_solver_decision,
    demo_supervisor_kickoff,
    demo_supervisor_review,
)


class LLMClientError(RuntimeError):
    """Raised when an LLM client cannot be configured or called."""


class BaseLLMClient:
    """Minimal chat interface used by the orchestrator."""

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


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


@dataclass(slots=True)
class OpenAICompatClient(BaseLLMClient):
    base_url: str
    api_key: str
    model: str

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("Missing LLM_BASE_URL.")
        if not self.api_key:
            raise ValueError("Missing LLM_API_KEY.")
        if not self.model:
            raise ValueError("Missing LLM_MODEL.")

        try:
            from openai import OpenAI  # type: ignore
        except ImportError as exc:
            raise LLMClientError(
                "The 'openai' package is required for real LLM calls."
            ) from exc

        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        timeout_sec: float = 30.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        for index, message in enumerate(messages):
            if not isinstance(message.get("content"), str):
                raise LLMClientError(
                    f"LLM request message[{index}].content must be a string."
                )

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout_sec,
        }
        if extra is not None:
            kwargs.update(extra)

        try:
            response = self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            raise LLMClientError(
                f"LLM request failed. model={self.model}, "
                f"base_url={self.base_url}, error={exc}"
            ) from exc

        if not response.choices:
            raise LLMClientError(
                f"LLM response has no choices. model={self.model}, "
                f"base_url={self.base_url}"
            )

        content = response.choices[0].message.content
        if not isinstance(content, str):
            raise LLMClientError(
                f"LLM response content is not a string. model={self.model}, "
                f"base_url={self.base_url}, content_type={type(content).__name__}"
            )
        return content


@dataclass(slots=True)
class DummyLLMClient(BaseLLMClient):
    """Deterministic local client that emits demo policy JSON only."""

    _supervisor_review_calls: int = field(default=0, init=False)

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout_sec: float = 1.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        del temperature, max_tokens, timeout_sec, extra
        if not messages:
            raise LLMClientError("DummyLLMClient requires at least one message.")
        prompt = messages[-1].get("content")
        if not isinstance(prompt, str):
            raise LLMClientError("DummyLLMClient requires string message content.")
        observation = _observation_from_prompt(prompt)
        if "ROLE: SUPERVISOR_KICKOFF" in prompt:
            return json.dumps(demo_supervisor_kickoff(observation), ensure_ascii=True)
        if "ROLE: SUPERVISOR_REVIEW" in prompt:
            self._supervisor_review_calls += 1
            return json.dumps(
                demo_supervisor_review(observation, stop=self._supervisor_review_calls > 1),
                ensure_ascii=True,
            )
        if "ROLE: SOLVER" in prompt:
            return json.dumps(demo_solver_decision(observation), ensure_ascii=True)
        raise LLMClientError("DummyLLMClient received an unknown prompt role.")


def _observation_from_prompt(prompt: str) -> Dict[str, Any]:
    marker = "CONTEXT:\n"
    schema_marker = "\n\nOUTPUT JSON SCHEMA:"
    if marker not in prompt or schema_marker not in prompt:
        return {}
    raw = prompt.split(marker, 1)[1].split(schema_marker, 1)[0]
    try:
        context = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    observation = context.get("observation", {}) if isinstance(context, dict) else {}
    return observation if isinstance(observation, dict) else {}


def build_llm_client(
    *,
    dummy: bool = False,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseLLMClient:
    if dummy:
        return DummyLLMClient()

    final_base_url = base_url.strip() if isinstance(base_url, str) else _env("LLM_BASE_URL")
    final_api_key = api_key.strip() if isinstance(api_key, str) else _env("LLM_API_KEY")
    final_model = model.strip() if isinstance(model, str) else _env("LLM_MODEL")

    if not final_base_url:
        raise ValueError("Missing LLM_BASE_URL.")
    if not final_api_key:
        raise ValueError("Missing LLM_API_KEY.")
    if not final_model:
        raise ValueError("Missing LLM_MODEL.")

    return OpenAICompatClient(
        base_url=final_base_url,
        api_key=final_api_key,
        model=final_model,
    )
