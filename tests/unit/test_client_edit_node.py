import pytest
import requests

from ska_src_site_capabilities_api.client.integration import SiteCapabilitiesIntegrationClient


def _client(monkeypatch, reads, fail_versions=()):
    """A client with no session: node reads come from ``reads``, writes with a version in ``fail_versions`` get a 409."""
    client = SiteCapabilitiesIntegrationClient.__new__(SiteCapabilitiesIntegrationClient)
    client.writes = []
    reads = iter(reads)
    monkeypatch.setattr(client, "_get_node", lambda node: next(reads))

    def update_node(node, payload):
        client.writes.append(payload)
        if payload["version"] in fail_versions:
            response = requests.Response()
            response.status_code = 409
            raise requests.HTTPError(response=response)

    monkeypatch.setattr(client, "update_node", update_node)
    monkeypatch.setattr("time.sleep", lambda s: None)
    return client


@pytest.mark.unit
def test_edit_node_rereads_and_retries_on_409(monkeypatch):
    client = _client(monkeypatch, [{"version": 1, "sites": [{"name": "A"}]}, {"version": 2, "sites": [{"name": "A"}]}], fail_versions={1})
    client.deregister_site("N", "A")
    assert [w["version"] for w in client.writes] == [1, 2]
    assert client.writes[-1]["sites"] == []


@pytest.mark.unit
def test_edit_node_gives_up_after_the_last_attempt(monkeypatch):
    client = _client(monkeypatch, [{"version": 1, "sites": []}] * 6, fail_versions={1})
    with pytest.raises(requests.HTTPError):
        client.deregister_site("N", "A")
    assert len(client.writes) == 6


@pytest.mark.unit
def test_edit_node_skips_the_write_when_there_is_nothing_to_change(monkeypatch):
    client = _client(monkeypatch, [{"version": 1, "sites": [{"name": "A"}]}])
    client.register_site("N", "A")
    assert client.writes == []
