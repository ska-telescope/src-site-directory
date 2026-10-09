# Developer guide

[TOC]

## Getting started

Contributions to this API are welcome. 

A contribution can be either be a patch or a minor/major feature. Patches include bugfixes and small changes to 
the code. Features can either be minor or major developments and can include potentially disruptive changes.

## Development environment

1. Clone the repository locally

```bash
git clone <ska-src-site-capabilities-api-url>
```

2. Initialise submodules for standard make targets and variables

```bash
ska-src-site-capabilities-api$ git submodule update --recursive --init
```

## Development cycle

Shared branch, release, and lock targets are defined in the `.make/srcnet.mk` submodule include.
This includes `lock`, `lock-server`, `lock-client`, `lock-check`, and `client-bump-<patch|minor|major>-release`.

Below Makefile targets are added on `ska-cicd-makefiles` submodules, include `srcnet.mk` in Makefile to use them. This is to facilitate easier and more consistent development. The general recipe is as follows:

1. Depending on what you are working on, fork the project and create a new major/minor/patch branch, e.g. 
   ```bash
   ska-src-site-capabilities-api$ make patch-branch NAME=some-name
   ```
   Note that this both creates and checkouts the branch.

2. Make your changes.


3. If you changed dependencies, update the lockfiles (`uv.lock` for the server, `uv.client.lock` for the client)
   ```bash
   ska-src-site-capabilities-api$ make lock
   ```
   Use `make lock-server` / `make lock-client` to update just one, `UV_LOCK_ARGS=--upgrade` to pass extra flags to
   `uv lock`, and `make lock-check` to verify both are up to date (also run in CI).
   
4. Add your changes to the branch:
    ```bash
   ska-src-site-capabilities-api$ git add ...
    ```
   
5. Bump the version and commit, entering a commit message when prompted:
    ```bash
   ska-src-site-capabilities-api$ make bump-and-commit
    ```
   This is essential to keep version numbers consistent across the helm chart and python package. It bumps the
   server only; the client is versioned independently (see [Releasing the client](#releasing-the-client)).
   
6. Push the changes to your fork when ready:
    ```bash
   ska-src-site-capabilities-api$ make push
    ```

7. Create a merge request against upstream main.

## Releasing the client

The client package (`pyproject.client.toml`, version tracked in `.release_client`) is released independently of the
server. Server releases are tagged `X.Y.Z`; client releases are tagged `client-X.Y.Z` and only build and publish the
client package.

1. Bump the client version using the appropriate release level:
   ```bash
   ska-src-site-capabilities-api$ make client-bump-patch-release   # or client-bump-minor-release / client-bump-major-release
   ```
   These targets update `.release_client`, `pyproject.client.toml` and `uv.client.lock`; they do not stage or commit changes.

2. Review the changes, then stage and commit them manually:
   ```bash
   ska-src-site-capabilities-api$ git add .release_client pyproject.client.toml uv.client.lock
   ska-src-site-capabilities-api$ git commit -m "Bump client release version"
   ```

3. Once merged, create the `client-X.Y.Z` tag in GitLab. The pipeline fails if the tag does not match the version in
   `pyproject.client.toml`.

## Development tricks

### Using uv

1. To install dependencies (including the `dev` group) from `uv.lock` into `.venv`:

```bash
ska-src-site-capabilities-api$ uv sync
```

2. To run a command inside the environment:

```bash
ska-src-site-capabilities-api$ uv run <command>
```

### Bypassing AuthN/Z

AuthN/Z can be bypassed **for development only** by setting `DISABLE_AUTHENTICATION=yes` in the environment.

## Schemas

It is recommended to record data in the document database by using the web frontend
(`/www/nodes/`, `/www/nodes/<node_name>`). These forms perform both client and server side verification of the input 
against the node schema at `etc/schemas/node.json` (which is, as an aside, constructed using 
other schemas in the same directory by referencing). For each record created or modified, a version number is 
incremented for the corresponding node and the input stored alongside the schema used to generate the form. All 
versions of a node specification are retained. Nodes can be added programmatically, but care should be taken to keep 
the input in line with the corresponding schema.

Schemas are flexible and new ones can be added/existing ones amended.

### Adding and amending schemas

To amend/add a new resource, the following checklist may be helpful:

- (adding only) Create the schema and add to the `etc/schemas` directory
- (amending only) Edit the corresponding schema in the `etc/schemas` directory
- Add/amend any models (`src/ska_src_site_capabilities_api/models`) 
- Amend the form UIs (`src/ska_src_site_capabilities_api/rest/static/js/add-node-form-ui.js`, `src/ska_src_site_capabilities_api/rest/static/js/edit-node-form-ui.js`)
- Amend the node template (`src/ska_src_site_capabilities_api/rest/templates/node.html`)
- Amend the REST server and backend (`src/ska_src_site_capabilities_api/rest/server.py`, `src/ska_src_site_capabilities_api/backend`):
    - Add/amend any routes and corresponding backend functions
    - (if a new section for routes has been defined) Add a new tag to the `openapi_schema` 
    - (if a new model has been created) Change `responses` in the `app` route decorator to reference the appropriate models
- (if a new route has been created or its signature modified) Check that the corresponding Permissions API policy has been added/amended
- Amend and unit/integration test assets to reflect these changes

## Testing

Testing is done via the `pytest` module, with code coverage provided by the `pytest-cov` module.

### Component testing

Component testing uses the integration environment to spin up local services for testing. The component tests 
implemented for this repository are stored under the `/tests/component` directory. These component tests are executed 
during the ``test`` stage of the CI/CD pipeline under the ``k8s-test-api-with-disabled-auth`` and 
``k8s-test-api-with-enabled-auth`` jobs.

#### Running component tests locally with the Integration Environment

To run component tests against a local instance using the integration environment:

1. **Start the API with authentication disabled:**
   ```bash
   # Set the Integration Environment to start SC_API and uncomment DISABLE_AUTHENTICATION: "yes" in scapi-docker-compose.yanml
   bash scripts/stack/start-stack.
   ```
2. **Set environment variables for the tests:**
   ```bash
   export DISABLE_AUTHENTICATION=yes
   export API_URL=http://localhost:8081/v1  
   ```

3. **Run the tests using uv:**
   ```bash
   # Run all component tests
   uv run pytest tests/component -m component -v --override-ini="addopts="
   
   # Run a specific test file
   uv run pytest tests/component/test_compute.py -m component -v --override-ini="addopts="
   
   # Run with logging
   uv run pytest tests/component -m component -v -s --log-cli-level=INFO --override-ini="addopts="
   ```

**Note:** The `--override-ini="addopts="` flag is needed to override pytest.ini default options that may cause issues 
in local testing.

#### Test data

The tests automatically load test data from `tests/assets/component/nodes.json` before running. This data is loaded via 
the `load_nodes_data` fixture defined in `conftest.py`. The fixture:
- Deletes existing nodes with the same names (if they exist)
- Loads all nodes from the JSON file
- Makes the data available for all component tests

#### Environment variables

- `API_URL`: Base API URL (default: `http://localhost:8080/v1` if not in Kubernetes)
  - **Important:** Adjust the port if your Docker container maps to a different port (e.g., `http://localhost:8081/v1`)
- `DISABLE_AUTHENTICATION`: Set to `yes` to disable authentication checks
  - **Important:** This must also be set in the Docker container environment (`DISABLE_AUTHENTICATION=yes`)

#### Running component tests locally with Kubernetes

For local testing in a Kubernetes environment, an environment can be installed via minikube/helm with:

```bash
ska-src-site-capabilities-api$ minikube start
ska-src-site-capabilities-api$ make k8s-install-chart
```

Note that if only tests are modified, it isn't necessary to run the `k8s-install-chart` target.

To run the tests locally with both authentication enabled and disabled, respectively:

```bash
ska-src-site-capabilities-api$ make k8s-test-auth
ska-src-site-capabilities-api$ make k8s-test-noauth
```

## Code quality

This repository uses [`ruff`](https://docs.astral.sh/ruff/) for both linting and formatting, configured under
`[tool.ruff]` in `pyproject.toml`.

### Linting

Operations for code linting are performed by the `python-lint` Makefile target provided by the `.make` submodule:

```bash
ska-src-site-capabilities-api$ make python-lint
```

### Formatting

Operations for code formatting are performed by the `python-format` Makefile target provided by the `.make` submodule:

```bash
ska-src-site-capabilities-api$ make python-format
```

## Documentation

There is a Makefile target for generating documentation locally:

```bash
ska-src-site-capabilities-api$ make docs-build html
```

This installs the `docs` dependency group into `.venv` before building.

To render inheritance diagrams etc., the `graphviz` library must be installed.
