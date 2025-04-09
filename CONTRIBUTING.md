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
ska-src-data-management-api$ git submodule update --recursive --init
```

## Development cycle

Makefile targets have been included to facilitate easier and more consistent development. The general recipe is as 
follows:

1. Depending on what you are working on, fork the project and create a new major/minor/patch branch, e.g. 
    ```bash
    ska-src-data-management-api$ make patch-branch NAME=some-name
    ```
    Note that this both creates and checkouts the branch.

2. Make your changes.

3. Create new (OpenAPI) code samples if necessary (requires the service to be running):
   ```bash
   ska-src-data-management-api$ make code-samples
   ```

4. Update `poetry.lock`
   ```bash
   ska-src-data-management-api$ poetry lock --no-update
   ```
   
5. Add your changes to the branch:
    ```bash
   ska-src-data-management-api$ git add ...
    ```
   
6. Bump the version and commit, entering a commit message when prompted:
    ```bash
   ska-src-data-management-api$ make bump-and-commit
    ```
   This is essential to keep version numbers consistent across the helm chart and python package.
   
7. Push the changes to your fork when ready:
    ```bash
   ska-src-data-management-api$ make push
    ```

8. Create a merge request against upstream main.

## Development tricks

### Using poetry

1. To work inside a poetry shell:

```bash
ska-src-data-management-api$ poetry shell
```

2. To install dependencies from `pyproject.toml`:

```bash
(venv)ska-src-data-management-api$ poetry install
```

### Bypassing AuthN/Z

AuthN/Z can be bypassed **for development only** by setting `DISABLE_AUTHENTICATION=yes` in the environment.

## Testing

Testing is done via the `pytest` module, with code coverage provided by the `pytest-cov` module.

### Component testing

Component testing is conducted inside a k8s deployment environment using mocked responses to external services.

The component tests implemented for this repository are stored under the `/tests/component` directory. These 
component tests are executed during the ``test`` stage of the CI/CD pipeline under the
``k8s-test-api-with-disabled-auth`` and ``k8s-test-api-with-enabled-auth`` jobs.

For local testing, an environment can be installed via minikube/helm with:

```bash
ska-src-data-management-api$ minikube start
ska-src-data-management-api$ make k8s-install-chart
ska-src-data-management-api$ make k8s-test
```

Note that if only tests are modified, it isn't necessary to run the `k8s-install-chart` target.

To run the tests locally with both authentication enabled and disabled, respectively:

```bash
ska-src-data-management-api$ make k8s-test-auth
ska-src-data-management-api$ make k8s-test-noauth
```

## Code quality

This repository uses the following libraries for code quality:

- ``isort`` for sorting imports,
- ``black`` to enforce a consistent coding style,
- ``flake8`` to check code base against coding style (PEP8), and
- ``pylint`` to look for programming errors and code smells

### Linting

Operations for code linting are performed by the `python-lint` Makefile target provided by the `.make` submodule. This 
should be run inside a poetry shell.

### Formatting

Operations for code formatting are performed by the `python-format` Makefile target provided by the `.make` submodule. This 
should be run inside a poetry shell.

## Documentation

There is a Makefile target for generating documentation locally:

```bash
ska-src-data-management-api/docs$ make html
```

To render inheritance diagrams etc., the `graphviz` library must be installed.
