# Developer guide

## Getting started

Contributions to this API are welcome. 

A contribution can be either be a patch or a minor/major feature. Patches include bugfixes and small changes to 
the code. Features can either be minor or major developments and can include potentially disruptive changes.

## Development environment

1. Clone the repository locally

```bash
git clone <ska-src-site-capabilities-api-url>
```

2. Add submodules for make targets and variables

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

### Bypassing AuthN/Z

AuthN/Z can be bypassed **for development only** by setting `DISABLE_AUTHENTICATION=yes` in the environment.

## Component testing

CI component testing is conducted inside a k8s deployment environment. This deployment environment can be installed 
locally via minikube/helm with:

```bash
ska-src-data-management-api$ minikube start
ska-src-data-management-api$ make k8s-install-chart
ska-src-data-management-api$ make k8s-test
```

Note that if only tests are modified, it isn't necessary to run the `k8s-install-chart` target.

## Code formatting and linting

Operations for code formatting and linting are provided by the `python-format` and `python-lint` Makefile targets. 
These targets are provided by the `.make` submodule. To use these targets, first initialise and update this submodule:

```bash
ska-src-data-management-api$ git submodule init && git submodule update
```

then create a virtual environment:

```bash
ska-src-data-management-api$ poetry shell
```

and install all the dependencies listed in `pyproject.toml`:

```bash
(venv)ska-src-data-management-api$ poetry install
```

To run code formatting checks:

```bash
ska-src-data-management-api$ make python-format
```

To run linting:

```bash
ska-src-data-management-api$ make python-lint
```

## Documentation

There is a Makefile target for generating documentation locally:

```bash
ska-src-data-management-api/docs$ make html
```

To render inheritance diagrams etc., the `graphviz` library must be installed.
