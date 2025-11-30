from datetime import datetime

import pytest

from funnels import purchase_sync_service
from funnels.purchase_sync_service import PurchaseSyncService


class DummyConnection:
    pass


class DummyBrevoClient:
    def create_or_update_contact(self, contact):
        pass


def test_purchase_sync_marks_entry_as_purchased(monkeypatch):
    pending_entries = [
        ("user@example.com", "language", None, 42),
    ]

    calls = {"marked": []}

    def fake_get_pending_funnel_entries(connection, max_rows):
        assert isinstance(connection, DummyConnection)
        assert max_rows == 100
        return pending_entries

    def fake_get_certificate_purchase_for_entry(
        connection, email, funnel_type, user_id, test_id
    ):
        assert email == "user@example.com"
        assert funnel_type == "language"
        assert test_id == 42
        return (123, datetime(2025, 1, 1, 12, 0, 0))

    def fake_mark_certificate_purchased(
        connection, email, funnel_type, test_id, purchased_at
    ):
        calls["marked"].append((email, funnel_type, test_id, purchased_at))

    monkeypatch.setattr(
        purchase_sync_service,
        "get_pending_funnel_entries",
        fake_get_pending_funnel_entries,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "get_certificate_purchase_for_entry",
        fake_get_certificate_purchase_for_entry,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "mark_certificate_purchased",
        fake_mark_certificate_purchased,
    )

    service = PurchaseSyncService(
        connection=DummyConnection(),  # type: ignore[arg-type]
        brevo_client=DummyBrevoClient(),  # type: ignore[arg-type]
        dry_run=False,
    )
    service.sync(max_rows=100)

    assert len(calls["marked"]) == 1
    email, funnel_type, test_id, purchased_at = calls["marked"][0]
    assert email == "user@example.com"
    assert funnel_type == "language"
    assert test_id == 42
    assert isinstance(purchased_at, datetime)


def test_purchase_sync_skips_when_no_purchase_found(monkeypatch):
    pending_entries = [
        ("user@example.com", "language", None, 42),
    ]

    calls = {"marked": []}

    def fake_get_pending_funnel_entries(connection, max_rows):
        return pending_entries

    def fake_get_certificate_purchase_for_entry(
        connection, email, funnel_type, user_id, test_id
    ):
        return None

    def fake_mark_certificate_purchased(
        connection, email, funnel_type, test_id, purchased_at
    ):
        calls["marked"].append((email, funnel_type, test_id, purchased_at))

    monkeypatch.setattr(
        purchase_sync_service,
        "get_pending_funnel_entries",
        fake_get_pending_funnel_entries,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "get_certificate_purchase_for_entry",
        fake_get_certificate_purchase_for_entry,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "mark_certificate_purchased",
        fake_mark_certificate_purchased,
    )

    service = PurchaseSyncService(
        connection=DummyConnection(),  # type: ignore[arg-type]
        brevo_client=DummyBrevoClient(),  # type: ignore[arg-type]
        dry_run=False,
    )
    service.sync(max_rows=100)

    assert calls["marked"] == []


def test_purchase_sync_raises_value_error_for_invalid_purchase_datetime(monkeypatch):
    pending_entries = [
        ("user@example.com", "language", 10, 42),
    ]

    def fake_get_pending_funnel_entries(connection, max_rows):
        return pending_entries

    def fake_get_certificate_purchase_for_entry(
        connection, email, funnel_type, user_id, test_id
    ):
        assert email == "user@example.com"
        assert funnel_type == "language"
        assert user_id == 10
        assert test_id == 42
        return (123, "2025-01-01")

    def fake_mark_certificate_purchased(
        connection, email, funnel_type, test_id, purchased_at
    ):
        raise AssertionError(
            "mark_certificate_purchased must not be called for invalid datetime"
        )

    monkeypatch.setattr(
        purchase_sync_service,
        "get_pending_funnel_entries",
        fake_get_pending_funnel_entries,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "get_certificate_purchase_for_entry",
        fake_get_certificate_purchase_for_entry,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "mark_certificate_purchased",
        fake_mark_certificate_purchased,
    )

    service = PurchaseSyncService(
        connection=DummyConnection(),  # type: ignore[arg-type]
        brevo_client=DummyBrevoClient(),  # type: ignore[arg-type]
        dry_run=False,
    )

    with pytest.raises(ValueError):
        service.sync(max_rows=100)


def test_purchase_sync_dry_run_does_not_update_database_or_brevo(monkeypatch):
    """Test that dry-run mode does not call mark_certificate_purchased or Brevo API."""
    pending_entries = [
        ("user@example.com", "language", None, 42),
    ]

    calls = {"marked": [], "brevo": []}

    def fake_get_pending_funnel_entries(connection, max_rows):
        return pending_entries

    def fake_get_certificate_purchase_for_entry(
        connection, email, funnel_type, user_id, test_id
    ):
        return (123, datetime(2025, 1, 1, 12, 0, 0))

    def fake_mark_certificate_purchased(
        connection, email, funnel_type, test_id, purchased_at
    ):
        calls["marked"].append((email, funnel_type, test_id, purchased_at))
        raise AssertionError(
            "mark_certificate_purchased must not be called in dry-run mode"
        )

    class DummyBrevoClientWithTracking:
        def create_or_update_contact(self, contact):
            calls["brevo"].append(contact)
            raise AssertionError(
                "Brevo API must not be called in dry-run mode"
            )

    monkeypatch.setattr(
        purchase_sync_service,
        "get_pending_funnel_entries",
        fake_get_pending_funnel_entries,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "get_certificate_purchase_for_entry",
        fake_get_certificate_purchase_for_entry,
    )
    monkeypatch.setattr(
        purchase_sync_service,
        "mark_certificate_purchased",
        fake_mark_certificate_purchased,
    )

    service = PurchaseSyncService(
        connection=DummyConnection(),  # type: ignore[arg-type]
        brevo_client=DummyBrevoClientWithTracking(),  # type: ignore[arg-type]
        dry_run=True,
    )
    service.sync(max_rows=100)

    # In dry-run mode, no DB writes or Brevo calls should occur
    assert len(calls["marked"]) == 0
    assert len(calls["brevo"]) == 0