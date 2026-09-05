"""Tests for the Ollama-based LLM assist module. All HTTP calls are
mocked/injected - these tests must (and do) pass without Ollama installed
or running anywhere.
"""

import requests

from linkage_lab import llm_assist


def test_parse_llm_response_accepts_valid_json():
    text = '{"same_person": true, "confidence": 0.87, "reasoning_summary": "Samme navn og adresse."}'
    result = llm_assist.parse_llm_response(text)
    assert isinstance(result, llm_assist.LlmVerdict)
    assert result.same_person is True
    assert result.confidence == 0.87


def test_parse_llm_response_strips_markdown_code_fence():
    text = '```json\n{"same_person": false, "confidence": 0.2, "reasoning_summary": "Forskellige erhverv."}\n```'
    result = llm_assist.parse_llm_response(text)
    assert isinstance(result, llm_assist.LlmVerdict)
    assert result.same_person is False


def test_parse_llm_response_rejects_malformed_json():
    result = llm_assist.parse_llm_response("dette er ikke json")
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "malformed_json"


def test_parse_llm_response_rejects_missing_keys():
    result = llm_assist.parse_llm_response('{"same_person": true}')
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "invalid_schema"


def test_parse_llm_response_rejects_confidence_out_of_range():
    text = '{"same_person": true, "confidence": 1.5, "reasoning_summary": "x"}'
    result = llm_assist.parse_llm_response(text)
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "invalid_schema"


def test_parse_llm_response_rejects_wrong_type_for_same_person():
    text = '{"same_person": "yes", "confidence": 0.5, "reasoning_summary": "x"}'
    result = llm_assist.parse_llm_response(text)
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "invalid_schema"


class _FakeResponse:
    def __init__(self, status_code=200, json_body=None, text=""):
        self.status_code = status_code
        self._json_body = json_body
        self.text = text

    def json(self):
        if self._json_body is None:
            raise ValueError("no json body")
        return self._json_body


def test_query_ollama_returns_verdict_on_success():
    def fake_post(url, payload):
        body = {"response": '{"same_person": true, "confidence": 0.9, "reasoning_summary": "Match."}'}
        return _FakeResponse(200, body)

    result = llm_assist.query_ollama("some prompt", http_post=fake_post)
    assert isinstance(result, llm_assist.LlmVerdict)
    assert result.confidence == 0.9


def test_query_ollama_handles_connection_error_gracefully():
    def fake_post(url, payload):
        raise requests.exceptions.ConnectionError("no server")

    result = llm_assist.query_ollama("some prompt", http_post=fake_post)
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "ollama_unavailable"


def test_query_ollama_handles_timeout_gracefully():
    def fake_post(url, payload):
        raise requests.exceptions.Timeout("too slow")

    result = llm_assist.query_ollama("some prompt", http_post=fake_post)
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "timeout"


def test_query_ollama_handles_non_200_status():
    def fake_post(url, payload):
        return _FakeResponse(500, text="internal error")

    result = llm_assist.query_ollama("some prompt", http_post=fake_post)
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "http_error"


def test_query_ollama_handles_unexpected_response_shape():
    def fake_post(url, payload):
        return _FakeResponse(200, {"unexpected": "shape"})

    result = llm_assist.query_ollama("some prompt", http_post=fake_post)
    assert isinstance(result, llm_assist.LlmError)
    assert result.reason == "malformed_json"


def test_is_ollama_available_returns_false_when_unreachable():
    assert llm_assist.is_ollama_available(url="http://localhost:1/api/tags", timeout=0.5) is False


def test_build_prompt_includes_both_records_and_json_instructions():
    prompt = llm_assist.build_prompt({"fornavn": "Jens"}, {"fornavn": "Jens"})
    assert "Jens" in prompt
    assert "same_person" in prompt
