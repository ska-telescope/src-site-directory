# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.54]

### Added

- Symlink in charts/ska-src-site-capabilities-api pointing to etc/helm, as release machinery from System assumes
  this location.

### Changed

- Makefile now uses System Makefile targets for release handling

### Removed

- VERSION now handled by pyproject.toml
- Reference to VERSION in Dockerfile init, now reference pyproject.toml
- etc/scripts/increment* scripts, now handled by System Makefile targets

## [0.3.53]

### Added

### Changed

- Removed redundant includes and parameters from Makefile, changed ordering and included comments.
- Dockerfile copy redundancy. Now only copy application files across once.

### Fixed

- PYTHON_LINE_LENGTH to Makefile

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