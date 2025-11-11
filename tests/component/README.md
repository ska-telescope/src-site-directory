# Component Tests

Component tests for the Site Capabilities API.

## Running Locally

To run component tests against a local Docker instance:

0. **Copy the .env.template to .env:**
    ```bash
    cp .env.template .env
    ```

1. **Start the API with authentication disabled:**
   ```bash
   # Using docker-compose.local.yml (recommended for testing)
   docker-compose -f docker-compose.local.yml up -d
   
   # Or ensure your running container has DISABLE_AUTHENTICATION=yes
   docker run -e DISABLE_AUTHENTICATION=yes -p 8081:8080 ...
   ```

2. **Set environment variables for the tests:**
   ```bash
   export DISABLE_AUTHENTICATION=yes
   export API_URL=http://localhost:8081/v1  # Adjust port if different
   ```

3. **Run the tests using Poetry:**
   ```bash
   # Run all component tests
   poetry run pytest tests/component -m component -v --override-ini="addopts="
   
   # Run a specific test file
   poetry run pytest tests/component/test_compute.py -m component -v --override-ini="addopts="
   
   # Run with logging
   poetry run pytest tests/component -m component -v -s --log-cli-level=INFO --override-ini="addopts="
   ```

### Example:

```bash
# Start API with authentication disabled
docker-compose -f docker-compose.local.yml up -d

# Set test environment
export DISABLE_AUTHENTICATION=yes
export API_URL=http://localhost:8081/v1

# Run tests
poetry run pytest tests/component -m component -v -s --log-cli-level=INFO --override-ini="addopts="
```

**Note:** The `--override-ini="addopts="` flag is needed to override pytest.ini default options that may cause issues in local testing.

## Test Data

The tests automatically load test data from `tests/assets/component/nodes.json` before running.
This data is loaded via the `load_nodes_data` fixture defined in `conftest.py`.

The fixture:
- Deletes existing nodes with the same names (if they exist)
- Loads all nodes from the JSON file
- Makes the data available for all component tests

## Environment Variables

- `API_URL`: Base API URL (default: `http://localhost:8080/v1` if not in Kubernetes)
  - **Important:** Adjust the port if your Docker container maps to a different port (e.g., `http://localhost:8081/v1`)
- `DISABLE_AUTHENTICATION`: Set to `yes` to disable authentication checks
  - **Important:** This must also be set in the Docker container environment (`DISABLE_AUTHENTICATION=yes`)
- `KUBE_NAMESPACE`: Kubernetes namespace (for Kubernetes environments)
- `CLUSTER_DOMAIN`: Kubernetes cluster domain (for Kubernetes environments)

## Running in Kubernetes

When `KUBE_NAMESPACE` and `CLUSTER_DOMAIN` are set, the tests will use the Kubernetes service URL format:
`http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1`

