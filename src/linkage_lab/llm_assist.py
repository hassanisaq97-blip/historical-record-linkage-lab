"""Experimental LLM-assisted linkage via a local Ollama server.

Scope, deliberately narrow (see docs/limitations.md for the full
discussion): this module never replaces the rule-based or ML linkage
methods. It is meant to be applied only to "gray zone" candidate pairs -
ones the ML model itself is least confident about (predicted probability
near the decision threshold) - as a supplementary, experimental signal.

Design goals:
- No paid API dependency: talks to a local Ollama server
  (https://ollama.com) over plain HTTP, matching the author's own prior
  experience running Llama 3.2 locally via Ollama rather than requiring
  an Anthropic/OpenAI API key.
- Never crashes the pipeline: connection errors, timeouts, malformed
  JSON, and schema-invalid output are all caught and turned into a
  well-typed "no verdict" result rather than an exception.
- Fully testable without Ollama installed or running: `query_ollama` and
  `classify_pair` are pure functions of an injectable HTTP call, so tests
  can substitute a fake transport (see tests/test_llm_assist.py).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

import requests

DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TIMEOUT_SECONDS = 30

REQUIRED_KEYS = {"same_person", "confidence", "reasoning_summary"}


@dataclass
class LlmVerdict:
    same_person: bool
    confidence: float
    reasoning_summary: str
    raw_response: str


@dataclass
class LlmError:
    reason: str  # "ollama_unavailable" | "timeout" | "malformed_json" | "invalid_schema" | "http_error"
    detail: str


SYSTEM_INSTRUCTIONS = """Du hjælper med historisk record linkage. Du får to strukturerede \
poster og skal vurdere, om de sandsynligvis beskriver samme virkelige person. \
Historiske kilder indeholder ofte stavevarianter, forkortelser og \
transskriptionsfejl - lad det ikke automatisk udelukke et match, men kræv \
også reelt sammenfald i navn og mindst ét understøttende felt (erhverv, \
adresse, alder/år).

Svar UDELUKKENDE med gyldig JSON i præcis dette format, uden forklarende \
tekst udenfor JSON'en:
{"same_person": true or false, "confidence": tal mellem 0.0 og 1.0, "reasoning_summary": "kort begrundelse paa max 2 saetninger"}"""


def build_prompt(record_a: dict[str, Any], record_b: dict[str, Any]) -> str:
    def _format(record: dict[str, Any]) -> str:
        return "\n".join(f"- {key}: {value}" for key, value in record.items() if value is not None)

    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"Post A:\n{_format(record_a)}\n\n"
        f"Post B:\n{_format(record_b)}\n"
    )


def parse_llm_response(text: str) -> LlmVerdict | LlmError:
    text = text.strip()
    # Ollama sometimes wraps JSON in markdown code fences despite instructions.
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()

    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return LlmError("malformed_json", text[:200])

    if not isinstance(payload, dict) or not REQUIRED_KEYS.issubset(payload.keys()):
        return LlmError("invalid_schema", f"missing keys, got: {list(payload) if isinstance(payload, dict) else type(payload)}")

    same_person = payload["same_person"]
    confidence = payload["confidence"]
    reasoning = payload["reasoning_summary"]

    if not isinstance(same_person, bool):
        return LlmError("invalid_schema", f"same_person must be bool, got {type(same_person)}")
    if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
        return LlmError("invalid_schema", f"confidence must be a number in [0,1], got {confidence!r}")
    if not isinstance(reasoning, str) or not reasoning.strip():
        return LlmError("invalid_schema", "reasoning_summary must be a non-empty string")

    return LlmVerdict(
        same_person=same_person,
        confidence=float(confidence),
        reasoning_summary=reasoning.strip(),
        raw_response=text,
    )


HttpPost = Callable[[str, dict], requests.Response]


def _default_http_post(url: str, payload: dict) -> requests.Response:
    return requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT_SECONDS)


def query_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    url: str = DEFAULT_OLLAMA_URL,
    http_post: HttpPost = _default_http_post,
) -> LlmVerdict | LlmError:
    payload = {"model": model, "prompt": prompt, "stream": False, "format": "json"}

    try:
        response = http_post(url, payload)
    except requests.exceptions.ConnectionError as exc:
        return LlmError("ollama_unavailable", str(exc))
    except requests.exceptions.Timeout as exc:
        return LlmError("timeout", str(exc))
    except requests.exceptions.RequestException as exc:
        return LlmError("http_error", str(exc))

    if response.status_code != 200:
        return LlmError("http_error", f"HTTP {response.status_code}: {response.text[:200]}")

    try:
        body = response.json()
        generated_text = body["response"]
    except (ValueError, KeyError) as exc:
        return LlmError("malformed_json", f"unexpected Ollama response shape: {exc}")

    return parse_llm_response(generated_text)


def classify_pair(
    record_a: dict[str, Any],
    record_b: dict[str, Any],
    model: str = DEFAULT_MODEL,
    url: str = DEFAULT_OLLAMA_URL,
    http_post: HttpPost = _default_http_post,
) -> LlmVerdict | LlmError:
    prompt = build_prompt(record_a, record_b)
    return query_ollama(prompt, model=model, url=url, http_post=http_post)


def is_ollama_available(url: str = "http://localhost:11434/api/tags", timeout: float = 3.0) -> bool:
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
