from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .demo_policy import (
    demo_build_initial_action,
    demo_objective_plan,
    demo_run_alns_action,
    demo_stop_action,
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

        # The caller owns the exact endpoint. This client does not append /v1,
        # rewrite URLs, or fall back to any other provider.
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
        """Call an OpenAI-compatible chat-completions endpoint.

        Args:
            messages: Chat messages with string `role` and `content` fields.
            temperature: Sampling temperature passed through to the provider.
            max_tokens: Maximum generated tokens.
            timeout_sec: Request timeout in seconds.
            extra: Optional provider-specific request fields.

        Returns:
            The model response text.

        Raises:
            LLMClientError: If the provider call fails or returns non-text
                content. The error includes the configured model and base URL.
        """
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

    _action_calls: int = field(default=0, init=False)

    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout_sec: float = 1.0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Return a fixed demo objective/action for smoke testing.

        Dummy mode never reads real LLM configuration and never imports the
        OpenAI SDK. It is intentionally labeled as a demo policy source in
        runner/orchestrator logs.
        """
        if not messages:
            raise LLMClientError("DummyLLMClient requires at least one message.")
        prompt = messages[-1].get("content")
        if not isinstance(prompt, str):
            raise LLMClientError("DummyLLMClient requires string message content.")

        import json

        if "choose a locked lexicographic objective" in prompt:
            return json.dumps(demo_objective_plan(), ensure_ascii=True)

        if self._action_calls == 0:
            self._action_calls += 1
            return json.dumps(demo_build_initial_action(), ensure_ascii=True)
        if self._action_calls == 1:
            self._action_calls += 1
            return json.dumps(demo_run_alns_action(), ensure_ascii=True)
        self._action_calls += 1
        return json.dumps(demo_stop_action(), ensure_ascii=True)


def build_llm_client(
    *,
    dummy: bool = False,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseLLMClient:
    """Build the LLM client used by the command-line runner.

    Args:
        dummy: When true, return `DummyLLMClient` without reading real LLM
            environment variables and without importing `openai`.
        base_url: Explicit endpoint override. If omitted, `LLM_BASE_URL` is
            read from the environment.
        api_key: Explicit API key override. If omitted, `LLM_API_KEY` is read.
        model: Explicit model override. If omitted, `LLM_MODEL` is read.

    Returns:
        A dummy or OpenAI-compatible client.

    Raises:
        ValueError: If real mode is selected and any required connection field
            is missing.
        LLMClientError: If the OpenAI SDK is unavailable in real mode.
    """
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
