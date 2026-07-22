from __future__ import annotations

from application import create_dashboard


def test_application_shell_and_health_endpoint():
    dashboard = create_dashboard()
    client = dashboard.server.test_client()
    page = client.get("/")
    health = client.get("/health")
    assert page.status_code == 200
    assert b"Mercora" in page.data
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"


def test_all_five_navigation_callbacks_are_registered():
    dashboard = create_dashboard()
    callback_inputs = " ".join(str(value.get("inputs", "")) for value in dashboard.callback_map.values())
    for navigation_id in ("nav-command", "nav-revenue", "nav-retention", "nav-customers", "nav-trust"):
        assert navigation_id in callback_inputs


def test_language_selector_and_persistent_store_are_present():
    dashboard = create_dashboard()
    callback_inputs = " ".join(str(value.get("inputs", "")) for value in dashboard.callback_map.values())
    assert "language-pt" in callback_inputs
    assert "language-en" in callback_inputs
    assert "language-store" in callback_inputs
