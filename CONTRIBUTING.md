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

### Bypassing AuthN/Z

AuthN/Z can be bypassed **for development only** by setting `DISABLE_AUTHENTICATION=yes` in the environment.

## Formatting and Linting

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

## Documentation

There is a Makefile target for generating documentation locally:

```bash
ska-src-data-management-api$ make docs
```

but you will need to ensure the necessary sphinx extensions are installed as these are not included in the core 
requirements.

## To build site capabilities docker image

```bash
ska-src-data-management-api$ make oci-image-build
```

## To install site capabilities deployment locally

```bash
ska-src-data-management-api$ make k8s-install-chart
```