# Developer guide

## Getting started

Contributions to this API are welcome. 

A contribution can be either be a patch or a minor/major feature. Patches include bugfixes and small changes to 
the code. Features can either be minor or major developments and can include potentially disruptive changes.

## Development cycle

Makefile targets have been included to facilitate easier and more consistent development. The general recipe is as 
follows:

1. Depending on what you are working on, fork the project and create a new major/minor/patch branch, e.g. 
    ```bash
    ska-src-data-management-api$ make patch-branch NAME=some-name
    ```
    Note that this both creates and checkouts the branch.

2. Make your changes.

3. Create new (OpenAPI) code samples if necessary (requires the service to be running).
   ```bash
   ska-src-data-management-api$ make code-samples
   ```
   
4. Add your changes to the branch:
    ```bash
   ska-src-data-management-api$ git add ...
    ```
   
5. Bump the version and commit, entering a commit message when prompted:
    ```bash
   ska-src-data-management-api$ make bump-and-commit
    ```
   This is essential to keep version numbers consistent across the helm chart and python package.
   
6. Push the changes to your fork when ready:
    ```bash
   ska-src-data-management-api$ make push
    ```

7. Create a merge request against upstream main
   
Note that the CI pipeline will fail if python packages with the same semantic version are committed to the GitLab 
Package Registry.

## Development tips

1. Clone the repository locally

git clone <site-capabilities-repository-url>

2. Add the submodules for make targets and variables

```bash
ska-src-data-management-api$ git submodule update --recursive --init
```
3. To create virtual env

```bash
ska-src-data-management-api$ poetry shell
```

4. To install dependencies from pyproject.toml

```bash
(venv)ska-src-data-management-api$ poetry install
```

### Bypassing AuthN/Z

AuthN/Z can be bypassed **for development only** by setting `DISABLE_AUTHENTICATION=yes` in the environment.


### Formatting and Linting

There is a makefile target to check formatting and linting for the code, create venv and execute below commands

To create virtual env

```bash
ska-src-data-management-api$ poetry shell
```

To install dependencies from pyproject.toml

```bash
(venv)ska-src-data-management-api$ poetry install
```

To do code formatting
```bash
ska-src-data-management-api$ make python-format
```

To do code linting
```bash
ska-src-data-management-api$ make python-lint
```

### Documentation

There is a Makefile target for generating documentation locally:

```bash
ska-src-data-management-api$ make docs
```

but you will need to ensure the necessary sphinx extensions are installed as these are not included in the core 
requirements.

### To build site capabilities docker image

```bash
ska-src-data-management-api$ make oci-image-build
```

### To install site capabilities deployment locally

```bash
ska-src-data-management-api$ make k8s-install-chart
```

### To uninstall site capabilities deployment locally

```bash
ska-src-data-management-api$ make k8s-uninstall-chart
```

## SKA SRC site capabilities api code quality guidelines

1. Code formatting / style

### Formatting

SKA SRC Site Capabilities API repository uses the ``black`` code formatter to format its code.
Formatting can be checked using command ``make python-format`` after creating venv.

The CI pipeline does check that if code has been formatted using black or not.

### Linting

SKA SRC Site Capabilities API repository uses below libraries/utilities for linting.
 Linting can be checked using command ``make python-lint`` after creating venv.

* ``isort`` - It provides a command line utility, Python library and 
    plugins for various editors to quickly sort all your imports.

* ``black`` - It is used to check if the code has been blacked.

* ``flake8`` - It is used to check code base against coding style (PEP8), 
    programming errors (like “library imported but unused” and “Undefined name”),etc.

* ``pylint`` - It is looks for programming errors, helps enforcing a coding standard, 
    sniffs for code smells and offers simple refactoring suggestions.

2. Test coverage

SKA SRC Site Capabilities API repository uses ``pytest`` to test its code, with the ``pytest-cov`` plugin for
measuring coverage.


## SKA SRC site capabilities api integration testing guidelines
The integration tests implemented for SKA SRC Site Capabilities API are present under /tests/integration folder.
Implemented integration tests covers positive scenarios for all API operations.

These Integrations tests get executed on pipeline in ``test`` stage under ``k8s-test-api-with-disabled-auth`` and ``k8s-test-api-with-enabled-auth`` jobs.
Tests get executed on pipeline using command `make k8s-test`.

All tests are implemented to verify below APIs including AUTHENTICATION as enabled and disabled.
For testing libraries like ``pytest``, ``httpx`` along with pytest plugins e.g ``pytest-cov`` ``pytest-json-report`` ``pytest-forked`` ``pytest-mock`` ``pytest-xdist`` ``pytest-repeat`` are used.


### APIs verified via tests

* ``get /health`` Test to verify Service health e.g ska-src-site-capabilities-api.

* ``get /ping`` Test to verify Service aliveness.

* ``get /sites``  Test to verify list sites operation.

* ``post /sites`` Test to verify new site is added via site json.

* ``delete /sites`` Test to verify Delete all sites operation.

* ``get /sites/{site}`` Test to verify Get all versions of site operation.

* ``delete /sites/{site}`` Test to verify Delete all versions of perticular site operation.

* ``get /sites/{site}/{version}`` Test to verify Get perticular version of perticular site operation.

* ``delete /sites/{site}/{version}`` Test to verify Delete perticular version of perticular site operation.

* ``get /sites/latest`` Test to verify Get latest versions of all sites operation.

* ``get /compute`` Test to verify List of all available computes operation.

* ``get /compute/{compute_id}`` Test to verify Get description of a compute element from a unique identifier operation.

* ``get /storages`` Test to verify List all storages operation.

* ``get /storages/{storage_id}`` Test to verify Get a storage description from a unique identifier operation.

* ``get /storages/grafana`` Test to verify List all storages in a format digestible by Grafana world map panels operation.

* ``get /storages/topojson`` Test to verify List all storages in topojson format operation.

* ``get /storage-areas`` Test to verify List all storage areas operation.

* ``get /storage-areas/{storage_area_id}`` Test to verify Get a storage area description from a unique identifier. operation.

* ``get /storage-areas/grafana`` Test to verify List all storage areas in a format digestible by Grafana world map panel operation.

* ``get /storage-areas/topojson`` Test to verify List all storage areas in topojson format operation.

* ``get /storage-areas/types`` Test to verify List storage area types operation.

* ``get /services`` Test to verify List all services operation.

* ``get /services/{service_id}`` Test to verify Get a service description from a unique identifier operation.

* ``get /services/types`` Test to verify List service types operation.

* ``get /schemas`` Test to verify Get a list of schema names used to define entities operation.

* ``get /schemas/{schema}`` Test to verify Get a schema by name operation.

