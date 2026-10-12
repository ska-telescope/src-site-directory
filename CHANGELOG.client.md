# Client Changelog

All notable changes to the client package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0]

### Added
- First release of the client package (`ska-src-site-capabilities-api-client`) as an independently versioned package, separate from the server package.

### Changed
- Breaking: client methods now propagate native `requests.HTTPError`, `requests.ConnectionError`, and `requests.Timeout` instead of wrapping errors in FastAPI's `HTTPException`. HTTP status and response content are available through `error.response.status_code` and `error.response.text`.
- Removed `ska-src-api-common` from client dependencies; the base client requires only `requests`. The optional `integration` extra still depends on the full Auth API package.
- Node registration now handles native HTTP errors without importing FastAPI.
