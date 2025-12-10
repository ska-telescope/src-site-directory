# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.81]

### Changed

- Refactored for routes

### Fixed

- grafana/topojson identifiers deprecated, now uses name attribute for element

## [0.3.80]

### Added

- Downtime form (credit Neon)

## [0.3.79]

### Changed

- Added etc/init/nodes_int.json for staging instance
- Change service types from LoadBalancer to NodePort

## [0.3.78]

### Changed

- Renamed compute-api to global-execution-api

## [0.3.77]

### Changed

- Updated `nodes.json` with 27-10-25 snapshot

## [0.3.76]

### Changed

- Changes to ensure that the SC dashboard to shows all data fields that were visible in the MR-based dashboard

## [0.3.75]

### Changed

- Updated `nodes.json` with 21-10-25 snapshot

## [0.3.74]

### Added

- Introduced `cavern` type in local services schema
- Introduced `compute-api` and `accounting-api` service types in global services schema

## [0.3.73]

### Changed

- Amending image registries for consistency

## [0.3.72]

### Changed

- Better handle IAM timeouts and pass exceptions as http error codes (use handle_exceptions decorator for all routes)

## [0.3.71]

### Added

- Topology endpoint

## [0.3.70]

### Removed

- Concept of service environments in favour of this being handled by separate deployments 

### Added

## [0.3.69]

### Added

- Parent site ids to respective elements (rather than just names)

## [0.3.68]

### Added

- `_get_service_labels_for_prometheus` to backend
- A pre-hook to CI that checks the branch's HEAD is up to date with main before building images

## [0.3.67]

### Changed

- Integration test asset paths

## [0.3.66]

### Added

- `compute_units` in compute schema

## [0.3.65]

### Added

- Service environments (int, prod, dev)
- Refactored bits of integration tests

## [0.3.64]

### Added

- for\_prometheus endpoints for services

## [0.3.63]

### Changed

- Amended integration tests

## [0.3.62]

### Changed

- Changes to CA requests bundle for intenv

## [0.3.61]

### Added

- First version of integration tests

### Changed

- Image build now uses same Dockerfile to create a branch-tagged version in the -integration repository
- Runner for join lint job now uses aws after cloud outage

## [0.3.60]

### Fixed

- Ingress issue in chart (missing host)

## [0.3.59]

### Added

- More code samples
- Deletion by node name endpoint
- Component tests now only run on success

### Changed

- Unit tests now marked as "unit"
- Typos in README and CONTRIBUTING

## [0.3.58]

### Added

- Introduced endpoints to enable/disable storage, compute, and site components:
  - `/sites/{site_id}/enabled` and `/sites/{site_id}/disabled`
  - `/compute/{compute_id}/enabled` and `/compute/{compute_id}/disabled`
  - `/storages/{storage_id}/enabled` and `/storages/{storage_id}/disabled`
- Added client methods corresponding to the new endpoints.
- Implemented unit tests to validate new backend methods.
- Added component tests to verify end-to-end flow, starting from the API call within the pipeline namespace.
- Integrated release automation for pipeline configuration.
- Added test for add_edit node

## [0.3.57]

### Added

- Introduced SKAO CI/CD component testing framework (credit: Shraddha B.):
  - Implemented secrets management for MongoDB and IAM credentials.
  - Updated Helm templates to use secrets as variables.
  - Integrated template repository for `make` targets (install/uninstall charts).
  - Configured deployments to install the site capabilities chart in a unique namespace per commit.
  - Added jobs to manually destroy the created namespaces.
  - Developed new component tests.
  - Set up a test-runner pod to execute tests.
  - Created separate jobs and namespaces for authentication-enabled and disabled test cases.
  - Documented the approach in ReadTheDocs.
  - Updated Helm configuration for GitLab pipeline to release and publish charts to the Central Artifact Repository (CAR).
- Streamlined Docker image:
  - Switched base from Debian Bullseye to Buster.
  - Removed MongoDB server installation.
  - Simplified Dockerfile layers.
- Fixed the `code-samples` target and added new route examples.
- Added schema migration tool (`0.3.56` → `0.3.57`) in `tools/`.
- Removed `only_` prefix from query parameters where appropriate.
- Renamed `identifier` to `name` to avoid conflicts with the `id` attribute.

## [0.3.56]

### Added

- Added backend unit tests.

## [0.3.56]

### Added

- New "Add Node" page at `/www/nodes`.
- New "Edit Node" page at `/www/nodes/<node_name>`.
- Added service type filtering to the "list services" endpoint.
- Enabled filtering by node and site names on relevant endpoints.

### Changed

- Restructured MongoDB to place nodes at the top level.
- Introduced `parent_*` IDs for sub-elements in list endpoints (for traceability).
- Renamed `disabled` to `is_force_disabled` for clarity.
- Updated all list endpoints to return a new response model.
- `site` now includes `site_id`, similar to other node child elements.
- Moved common functions from `server.py` to `common/utility.py`.
- Separated backend collections into archival and current.
- Expanded `/www/docs/user` with additional routes.

### Removed

- Removed ability to add a site directly; this is now done via `/www/nodes/<node_name>`.

## [0.3.55]

### Added

- Redirect from `/www/sites/add/<site>` if user is not logged in.
- Token expiration warnings and countdown timer.
- Added `downtime` and `disabled` fields for all entities.
- Favicon added to site HTML.
- Server-side constraint to enforce unique `node_name`.

### Changed

- `tier` value is now an integer instead of a string.
- Improved CSS layout for nested fieldsets.
- Global services are now included under compute.
- Renamed `associated_compute_id` and `associate_storage_id` to `parent_compute_id` and `parent_storage_id`.
- Updated "list services" endpoint to accept `service_scope` (`all`, `local`, or `global`).
- Changed compute `hardware_type` from checkbox array to a radio button.
- Refreshed outdated models.

### Fixed

- Set default items to `0` in tab arrays (line 2456 of `jsonform`).
- Addressed issue with hidden tabs in Chrome causing non-focusable validation errors—location of the error is now clearly displayed.

### Removed

- Removed tier titles from forms.
- Removed `via_proxy` flag from schemas.

## [0.3.54]

### Added

- Created symlink at `charts/ska-src-site-capabilities-api` pointing to `etc/helm`, as expected by release tooling.

### Changed

- Updated Makefile to use System targets for release processes.
- Dockerfile now pulls version from `pyproject.toml`.
- `docs/conf.py` now references the version from `pyproject.toml`.

### Removed

- Removed `VERSION` file; now managed via `pyproject.toml`.
- Removed `etc/scripts/increment*`; functionality now handled by System Makefile targets.

## [0.3.53]

### Changed

- Removed redundant includes and parameters from Makefile; added comments and reordered sections.
- Optimized Dockerfile to copy application files only once.

### Fixed

- Defined `PYTHON_LINE_LENGTH` in Makefile.




