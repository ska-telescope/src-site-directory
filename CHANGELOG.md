# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.57]

### Added

- SKAO CI/CD integration testing framework (credit Shraddha B.)

## [0.3.56]

### Added

- Unit tests for backend.

## [0.3.56]

### Added

- New add node landing page at www/nodes.
- New edit node landing page at www/nodes/<node_name>.
- Filtering for service types on list services endpoint.
- Filtering for node and site names on all relevant endpoints.

### Changed

- Restructed MongoDB database to have nodes at top level.
- Added concept of parent_* ids for subelements in list endpoints (for traceability).
- Renamed disabled to is_force_disabled for clarity.
- All list endpoints now have a different model response.
- Site now includes site_id (like other child elements of node).
- Added some common functions in server.py to common/utility.py.
- Two collections in backend now used, one for archival documents and one for latest.
- Added more routes to /www/docs/user page.

### Removed

- Ability to add_site, this is now done through /www/nodes/<node_name>.

## [0.3.55]

### Added

- Redirect from www/sites/add/<site> when not logged in.
- Token expiration warnings and timer.
- Downtime/disabled fields for all entities.
- Favicon to site html.
- Server side constraint on node_name being unique

### Changed

- Tier value is now integer, not string.
- CSS layout to be a bit more clear for nested fieldsets.
- Global services now part of compute.
- Name of associated_compute_id or associate_storage_id to parent_compute_id and parent_storage_id.
- List services endpoint now takes service_scope (all||local||global).
- Compute hardware_type changed from checkbox to radio (no longer array).
- Updated out of date models.

### Fixed

- Set default items in tabarrays to 0 (ln2456 of jsonform).
- Issue around non-focusable elements with hidden tabs in Chrome. Location of validation error now presented in box.

### Removed

- Tier titles from form.
- via_proxy flag from schemas.

## [0.3.54]

### Added

- Symlink in charts/ska-src-site-capabilities-api pointing to etc/helm, as release machinery from System assumes
  this location.

### Changed

- Makefile now uses System Makefile targets for release handling.
- Reference to VERSION in Dockerfile init, now references version in pyproject.toml.
- Reference to VERSION in docs/conf.py, now references version in pyproject.toml.

### Removed

- VERSION now handled by pyproject.toml.
- etc/scripts/increment* scripts, now handled by System Makefile targets.

## [0.3.53]

### Added

### Changed

- Removed redundant includes and parameters from Makefile, changed ordering and included comments.
- Dockerfile copy redundancy. Now only copy application files across once.

### Fixed

- PYTHON_LINE_LENGTH to Makefile.

### Removed

- helm-install target (for now).

## [0.3.52]

### Added

- svc.api.iam_client_id to client-credentials secret.
- Sessions secret key as secret.

### Changed

- CONTRIBUTING docs to reference how to initialise .make repo.
- Author in pyproject.toml to Rob B.
- conf.py now takes version and release from VERSION file.
- values.yaml to be backwards compatible with existing methodology, allowing secret to be specified in yaml.
- Single secret for both iam/mongo to be two separate ones (separation of concerns).

### Removed

- Duplication of CONTRIBUTING in docs by making include to base of repo.
- conf.py duplicate directives, e.g. exclude_patterns.
- Reference to SRCNet in class SiteCapabilitiesClient docstrings (in case of service being used outside of SRCNet context).
