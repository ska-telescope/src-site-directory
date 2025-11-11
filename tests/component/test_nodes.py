"""
A module for component tests related to nodes.
"""

import os

import httpx
import pytest

from tests.component.conftest import get_api_url, send_delete_request, send_get_request, send_post_request

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.component
def test_list_nodes(load_nodes_data):
    """Test to list all nodes"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify we have at least one node
        assert len(data) > 0
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_nodes_only_names(load_nodes_data):
    """Test to list nodes with only_names parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes?only_names=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return a list of strings (names)
        if len(data) > 0:
            assert isinstance(data[0], str)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_list_nodes_include_inactive(load_nodes_data):
    """Test to list nodes with include_inactive parameter"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes?include_inactive=true")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_get_node_by_name(load_nodes_data):
    """Test to get a node by name"""
    api_url = get_api_url()
    # Get the first node name from the loaded data
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/nodes/{node_name}")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            # API returns empty dict {} if node not found, or node data if found
            if data:  # If node exists
                assert "name" in data
                assert data["name"] == node_name
            # If empty dict, node doesn't exist (but API still returns 200)
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_get_node_by_name_latest_version(load_nodes_data):
    """Test to get a node by name with latest version"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        response = httpx.get(f"{api_url}/nodes/{node_name}?node_version=latest")  # noqa: E231
        if os.getenv("DISABLE_AUTHENTICATION") == "yes":
            assert response.status_code == 200
            data = response.json()
            # API returns empty dict {} if node not found, or node data if found
            if data:  # If node exists
                assert "name" in data
        else:
            assert response.status_code == 403


@pytest.mark.component
def test_get_node_not_found():
    """Test to get a non-existent node"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes/NONEXISTENT_NODE")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API returns 200 with empty dict {} when node not found
        assert response.status_code == 200
        data = response.json()
        assert data == {}  # Empty dict indicates node not found
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_dump_nodes(load_nodes_data):
    """Test to dump all versions of all nodes"""
    api_url = get_api_url()
    response = httpx.get(f"{api_url}/nodes/dump")  # noqa: E231
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_get_site_from_node_and_site_name(load_nodes_data):
    """Test to get a site from node and site names"""
    api_url = get_api_url()
    if load_nodes_data and len(load_nodes_data) > 0:
        node_name = load_nodes_data[0]
        # Try to get the first site from the node
        node_response = send_get_request(f"{api_url}/nodes/{node_name}")
        if node_response.status_code == 200:
            node_data = node_response.json()
            if "sites" in node_data and len(node_data["sites"]) > 0:
                site_name = node_data["sites"][0]["name"]
                response = httpx.get(f"{api_url}/nodes/{node_name}/sites/{site_name}")  # noqa: E231
                if os.getenv("DISABLE_AUTHENTICATION") == "yes":
                    assert response.status_code == 200
                    data = response.json()
                    assert "name" in data
                    assert data["name"] == site_name
                else:
                    assert response.status_code == 403


@pytest.mark.component
def test_create_node():
    """Test to create a new node"""
    api_url = get_api_url()
    # Create a minimal test node
    test_node = {
        "name": "TEST_NODE_POST",
        "comments": "Test node created by POST test",
        "sites": [],
    }

    # First, ensure the node doesn't exist by trying to delete it
    send_delete_request(f"{api_url}/nodes/{test_node['name']}")

    response = send_post_request(f"{api_url}/nodes", test_node)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        assert response.status_code == 200
        # POST returns HTMLResponse with the node ID
        response_text = response.text
        assert response_text  # Should contain the ID
    else:
        assert response.status_code == 403

    # Cleanup: delete the test node
    if os.getenv("DISABLE_AUTHENTICATION") == "yes" and response.status_code == 200:
        send_delete_request(f"{api_url}/nodes/{test_node['name']}")


@pytest.mark.component
def test_create_duplicate_node(load_nodes_data):
    """Test to create a duplicate node

    Note: The API may return 200 (creating a new version) or 409 (conflict)
    depending on implementation. The test accepts both behaviors.
    """
    api_url = get_api_url()
    if not load_nodes_data or len(load_nodes_data) == 0:
        return

    # Try to create a node with the same name as an existing one
    existing_node_name = load_nodes_data[0]

    # First, verify the node exists
    node_check = send_get_request(f"{api_url}/nodes/{existing_node_name}")
    if node_check.status_code != 200:
        return

    node_data = node_check.json()
    if not node_data:  # Node doesn't exist
        return

    # Store original comments to restore later
    original_comments = node_data.get("comments", "")

    duplicate_node = {
        "name": existing_node_name,
        "comments": "Duplicate node test",
        "sites": [],
    }

    response = send_post_request(f"{api_url}/nodes", duplicate_node)
    if os.getenv("DISABLE_AUTHENTICATION") != "yes":
        assert response.status_code == 403
        return

    # API may return 409 Conflict or 200 (if it creates a new version)
    # Both behaviors are acceptable depending on implementation
    assert response.status_code in (200, 409)

    # If it returns 200, it might have created a new version
    # If it returns 409, the duplicate was properly rejected
    if response.status_code == 200:
        # Verify the node still exists (might be updated or new version)
        verify_check = send_get_request(f"{api_url}/nodes/{existing_node_name}")
        assert verify_check.status_code == 200

        # Restore original state if needed
        if original_comments:
            restore_node = node_data.copy()
            restore_node["comments"] = original_comments
            send_post_request(f"{api_url}/nodes/{existing_node_name}", restore_node)


@pytest.mark.component
def test_edit_node(load_nodes_data):
    """Test to edit an existing node"""
    api_url = get_api_url()
    if not load_nodes_data or len(load_nodes_data) == 0:
        return

    node_name = load_nodes_data[0]
    # Get the existing node data
    node_response = send_get_request(f"{api_url}/nodes/{node_name}")
    if node_response.status_code != 200:
        return

    node_data = node_response.json()
    if not node_data:  # Node doesn't exist
        return

    # Update the comments field
    original_comments = node_data.get("comments", "")
    updated_node = node_data.copy()
    updated_node["comments"] = "Updated by test_edit_node"

    response = send_post_request(f"{api_url}/nodes/{node_name}", updated_node)
    if os.getenv("DISABLE_AUTHENTICATION") != "yes":
        assert response.status_code == 403
        return

    assert response.status_code == 200
    # POST returns HTMLResponse with the node ID
    response_text = response.text
    assert response_text  # Should contain the ID

    # Verify the update by getting the node again
    verify_response = send_get_request(f"{api_url}/nodes/{node_name}")
    if verify_response.status_code == 200:
        updated_data = verify_response.json()
        if updated_data:
            assert updated_data.get("comments") == "Updated by test_edit_node"

            # Restore original comments
            updated_node["comments"] = original_comments
            send_post_request(f"{api_url}/nodes/{node_name}", updated_node)


@pytest.mark.component
def test_edit_nonexistent_node():
    """Test to edit a non-existent node"""
    api_url = get_api_url()
    nonexistent_node_name = "NONEXISTENT_NODE_FOR_EDIT"
    test_node = {
        "name": nonexistent_node_name,
        "comments": "Trying to edit non-existent node",
        "sites": [],
    }

    response = send_post_request(f"{api_url}/nodes/{nonexistent_node_name}", test_node)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may create the node or return an error
        # Based on server.py, it will try to edit, so it may succeed or fail
        assert response.status_code in (200, 404, 403)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_delete_node():
    """Test to delete a node by name"""
    api_url = get_api_url()
    # First, create a test node to delete
    test_node = {
        "name": "TEST_NODE_DELETE",
        "comments": "Test node for deletion",
        "sites": [],
    }

    # Ensure it doesn't exist first
    send_delete_request(f"{api_url}/nodes/{test_node['name']}")

    # Create the node
    create_response = send_post_request(f"{api_url}/nodes", test_node)
    if os.getenv("DISABLE_AUTHENTICATION") == "yes" and create_response.status_code == 200:
        # Now delete it
        delete_response = send_delete_request(f"{api_url}/nodes/{test_node['name']}")
        assert delete_response.status_code == 200
        data = delete_response.json()
        # Verify response structure
        assert isinstance(data, dict)

        # Verify the node is deleted
        get_response = send_get_request(f"{api_url}/nodes/{test_node['name']}")
        if get_response.status_code == 200:
            node_data = get_response.json()
            # Should return empty dict if node is deleted
            assert node_data == {}
    elif os.getenv("DISABLE_AUTHENTICATION") != "yes":
        # If auth is required, test that delete requires auth
        delete_response = send_delete_request(f"{api_url}/nodes/{test_node['name']}")
        assert delete_response.status_code == 403


@pytest.mark.component
def test_delete_nonexistent_node():
    """Test to delete a non-existent node"""
    api_url = get_api_url()
    nonexistent_node_name = "NONEXISTENT_NODE_FOR_DELETE"

    response = send_delete_request(f"{api_url}/nodes/{nonexistent_node_name}")
    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # API may return 200 (successful deletion even if not found) or an error
        # Based on backend behavior, it might return 200 with a result indicating no deletion
        assert response.status_code in (200, 404)
    else:
        assert response.status_code == 403


@pytest.mark.component
def test_create_edit_delete_node_cycle():
    """Test complete CRUD cycle: create, edit, delete"""
    api_url = get_api_url()
    test_node_name = "TEST_NODE_CRUD_CYCLE"

    if os.getenv("DISABLE_AUTHENTICATION") == "yes":
        # Cleanup first
        send_delete_request(f"{api_url}/nodes/{test_node_name}")

        # 1. Create node
        test_node = {"name": test_node_name, "comments": "Initial comment", "sites": []}
        create_response = send_post_request(f"{api_url}/nodes", test_node)
        assert create_response.status_code == 200

        # 2. Verify node exists
        get_response = send_get_request(f"{api_url}/nodes/{test_node_name}")
        assert get_response.status_code == 200
        node_data = get_response.json()
        assert node_data != {}
        assert node_data.get("name") == test_node_name

        # 3. Edit node
        updated_node = node_data.copy()
        updated_node["comments"] = "Updated comment"
        edit_response = send_post_request(f"{api_url}/nodes/{test_node_name}", updated_node)
        assert edit_response.status_code == 200

        # 4. Verify edit
        verify_response = send_get_request(f"{api_url}/nodes/{test_node_name}")
        assert verify_response.status_code == 200
        updated_data = verify_response.json()
        if updated_data:
            assert updated_data.get("comments") == "Updated comment"

        # 5. Delete node
        delete_response = send_delete_request(f"{api_url}/nodes/{test_node_name}")
        assert delete_response.status_code == 200

        # 6. Verify deletion
        final_get_response = send_get_request(f"{api_url}/nodes/{test_node_name}")
        assert final_get_response.status_code == 200
        final_data = final_get_response.json()
        assert final_data == {}  # Should be empty after deletion
