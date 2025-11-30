import logging
from typing import Any, Dict, Optional

import requests

from brevo.models import BrevoContact


class BrevoClientError(Exception):
    """Base exception for all Brevo client errors."""


class BrevoTransientError(BrevoClientError):
    """Error that is safe to retry later.

    This includes network issues, rate limiting (429), and server errors (5xx).
    """


class BrevoFatalError(BrevoClientError):
    """Error that should not be retried.

    This includes most 4xx client errors (except 429 which is transient).
    """


class BrevoApiClient:
    """HTTP client for Brevo (formerly Sendinblue) email marketing API.

    Handles all external API communication with Brevo, including contact management.
    In dry-run mode, all requests are logged but not executed, allowing safe testing
    without side effects.
    """

    def __init__(self, api_key: str, base_url: str, dry_run: bool) -> None:
        """Initializes the Brevo API client.

        Args:
            api_key: Brevo API key from account settings. Must be non-empty
                unless dry_run is True.
            base_url: Base URL for Brevo API (typically https://api.brevo.com/v3).
                Trailing slashes are automatically stripped.
            dry_run: If True, all API calls are logged but not executed.
                Used for testing without creating real contacts or consuming API quota.
        """
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.dry_run = dry_run
        self.logger = logging.getLogger("brevo.api_client")

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Performs HTTP request to Brevo API or logs it in dry-run mode.

        Side Effects:
            - In production mode: Makes actual HTTP request to Brevo API.
            - In dry-run mode: Only logs the request without executing it.

        Edge cases:
            - Empty API key raises RuntimeError (except in dry-run mode).
            - HTTP errors are classified as transient (429, 5xx) or fatal (other 4xx).
            - Network failures raise BrevoTransientError.
            - Invalid JSON responses return empty dict instead of crashing.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API endpoint path (e.g., "/contacts"). Leading slash is added
                automatically if missing.
            json_body: Optional JSON payload for request body.

        Returns:
            Response JSON as dictionary. Empty dict if response is not valid JSON.
            In dry-run mode, returns {"dry_run": True}.

        Raises:
            RuntimeError: If API key is missing (non-dry-run).
            BrevoTransientError: If network request fails or API returns 429/5xx.
            BrevoFatalError: If API returns 4xx (except 429).
        """
        url = self._build_url(path)
        if self.dry_run:
            self.logger.info(
                "Brevo dry run request: %s %s payload=%s",
                method,
                url,
                json_body,
            )
            return {"dry_run": True}

        if not self.api_key:
            raise RuntimeError("Brevo API key is not configured")

        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_body,
                timeout=10,
            )
        except requests.RequestException as error:
            self.logger.error("Brevo request error: %s", error)
            raise BrevoTransientError(f"Network error: {error}") from error

        if response.status_code >= 400:
            # Trim response body for error messages (limit to 500 chars)
            original_text = response.text if response.text else ""
            if len(original_text) > 500:
                response_text = original_text[:500] + "..."
            else:
                response_text = original_text

            if response.status_code == 429 or response.status_code >= 500:
                self.logger.error(
                    "Brevo API transient error %s: %s",
                    response.status_code,
                    response_text,
                )
                raise BrevoTransientError(
                    f"Brevo API error {response.status_code}: {response_text}"
                )
            else:
                # Other 4xx errors are fatal
                self.logger.error(
                    "Brevo API fatal error %s: %s",
                    response.status_code,
                    response_text,
                )
                raise BrevoFatalError(
                    f"Brevo API error {response.status_code}: {response_text}"
                )

        try:
            return response.json()  # type: ignore[no-any-return]
        except ValueError:
            return {}  # type: ignore[return-value]

    def create_or_update_contact(self, contact: BrevoContact) -> Dict[str, Any]:
        """Creates or updates a contact in Brevo (upsert operation).

        This is an upsert: if contact with the email exists, it's updated;
        otherwise, a new contact is created. The operation is idempotent:
        calling multiple times with the same email produces the same result.

        Side Effects:
            - Creates or updates contact in Brevo (unless dry-run mode).
            - Adds contact to specified lists if list_ids are provided.
            - Updates contact attributes if provided.

        Args:
            contact: BrevoContact object containing email, list IDs, and attributes.

        Returns:
            API response dictionary. In dry-run mode, returns {"dry_run": True}.

        Raises:
            BrevoTransientError: If network error or API returns 429/5xx.
            BrevoFatalError: If API returns 4xx (except 429).
        """
        payload = contact.to_payload()
        self.logger.info(
            "Sending contact to Brevo (email=%s, lists=%s, dry_run=%s)",
            contact.email,
            contact.list_ids,
            self.dry_run,
        )
        return self._request("POST", "/contacts", json_body=payload)
