import pytest
import requests

from brevo.models import BrevoContact
from brevo.api_client import BrevoApiClient, BrevoFatalError, BrevoTransientError


def test_create_or_update_contact_sends_correct_request(monkeypatch):
    calls = {}

    import brevo.api_client as api_module

    def fake_request(method, url, headers=None, json=None, timeout=None):
        calls["method"] = method
        calls["url"] = url
        calls["headers"] = headers
        calls["json"] = json

        class DummyResponse:
            def __init__(self):
                self.status_code = 200
                self.text = "ok"

            def json(self):
                return {"success": True}

        return DummyResponse()

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    client = BrevoApiClient(
        api_key="secret-key",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    contact = BrevoContact(
        email="user@example.com",
        list_ids=[1, 2],
        attributes={"FUNNEL_TYPE": "language"},
    )

    response = client.create_or_update_contact(contact)

    assert calls["method"] == "POST"
    assert calls["url"].endswith("/contacts")
    assert "api-key" in calls["headers"]
    assert calls["headers"]["api-key"] == "secret-key"
    assert calls["json"]["email"] == "user@example.com"
    assert calls["json"]["listIds"] == [1, 2]
    assert calls["json"]["attributes"]["FUNNEL_TYPE"] == "language"
    assert response == {"success": True}


def test_request_raises_runtime_error_when_api_key_missing(monkeypatch):
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    def fake_request(method, url, headers=None, json=None, timeout=None):
        raise AssertionError(
            "requests.request must not be called when api key is missing"
        )

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    with pytest.raises(RuntimeError):
        client._request("POST", "/contacts", json_body={"email": "user@example.com"})


def test_request_in_dry_run_mode_does_not_call_requests(monkeypatch):
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="",
        base_url="https://api.brevo.com/v3",
        dry_run=True,
    )

    def fake_request(method, url, headers=None, json=None, timeout=None):
        raise AssertionError("requests.request must not be called in dry_run mode")

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    response = client._request(
        "POST", "/contacts", json_body={"email": "user@example.com"}
    )

    assert response == {"dry_run": True}


def test_request_raises_brevo_transient_error_on_network_exception(monkeypatch):
    """Test that network exceptions raise BrevoTransientError."""
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="secret-key",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    def fake_request(method, url, headers=None, json=None, timeout=None):
        raise requests.ConnectionError("Connection failed")

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    with pytest.raises(BrevoTransientError) as exc_info:
        client._request("POST", "/contacts", json_body={"email": "user@example.com"})

    assert "Network error" in str(exc_info.value)
    assert "Connection failed" in str(exc_info.value)


def test_request_raises_brevo_transient_error_on_429(monkeypatch):
    """Test that HTTP 429 raises BrevoTransientError."""
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="secret-key",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    class DummyResponse:
        def __init__(self):
            self.status_code = 429
            self.text = "Rate limit exceeded"

        def json(self):
            return {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    with pytest.raises(BrevoTransientError) as exc_info:
        client._request("POST", "/contacts", json_body={"email": "user@example.com"})

    assert "429" in str(exc_info.value)
    assert "Rate limit exceeded" in str(exc_info.value)


def test_request_raises_brevo_transient_error_on_5xx(monkeypatch):
    """Test that HTTP 5xx raises BrevoTransientError."""
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="secret-key",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    class DummyResponse:
        def __init__(self):
            self.status_code = 500
            self.text = "Internal server error"

        def json(self):
            return {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    with pytest.raises(BrevoTransientError) as exc_info:
        client._request("POST", "/contacts", json_body={"email": "user@example.com"})

    assert "500" in str(exc_info.value)
    assert "Internal server error" in str(exc_info.value)


def test_request_raises_brevo_fatal_error_on_4xx(monkeypatch):
    """Test that HTTP 4xx (except 429) raises BrevoFatalError."""
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="secret-key",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    class DummyResponse:
        def __init__(self):
            self.status_code = 400
            self.text = "Bad request"

        def json(self):
            return {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    with pytest.raises(BrevoFatalError) as exc_info:
        client._request("POST", "/contacts", json_body={"email": "user@example.com"})

    assert "400" in str(exc_info.value)
    assert "Bad request" in str(exc_info.value)


def test_request_raises_brevo_fatal_error_on_404(monkeypatch):
    """Test that HTTP 404 raises BrevoFatalError."""
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="secret-key",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    class DummyResponse:
        def __init__(self):
            self.status_code = 404
            self.text = "Not found"

        def json(self):
            return {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    with pytest.raises(BrevoFatalError) as exc_info:
        client._request("POST", "/contacts", json_body={"email": "user@example.com"})

    assert "404" in str(exc_info.value)
    assert "Not found" in str(exc_info.value)


def test_request_trims_long_response_body(monkeypatch):
    """Test that long response bodies are trimmed in error messages."""
    import brevo.api_client as api_module

    client = BrevoApiClient(
        api_key="secret-key",
        base_url="https://api.brevo.com/v3",
        dry_run=False,
    )

    long_text = "x" * 1000

    class DummyResponse:
        def __init__(self):
            self.status_code = 400
            self.text = long_text

        def json(self):
            return {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr(api_module.requests, "request", fake_request)

    with pytest.raises(BrevoFatalError) as exc_info:
        client._request("POST", "/contacts", json_body={"email": "user@example.com"})

    error_message = str(exc_info.value)
    assert len(error_message) < len(long_text) + 50  # Should be trimmed
    assert "..." in error_message  # Should have ellipsis
