# Set build context as PWD for multiple images
OCI_IMAGE_BUILD_CONTEXT = $(PWD)

# Build additional tag for integration environment (oci.mk)
OCI_BUILD_ADDITIONAL_TAGS = $(CI_COMMIT_REF_SLUG)

# Docs are built with the 'docs' dependency group (docs.mk)
DOCS_PYTHON_RUNNER := uv run python3

docs-pre-build:
	uv sync --group docs

# bump-and-commit (srcnet.mk) must also stage uv.lock, which python-set-release updates
BUMP_FILES = .release $(CHART_YAML) pyproject.toml uv.lock

# Bespoke partial Makefiles
include testing.mk		# add testing settings and targets
ifneq ($(CI_JOB_ID),)
  include cicd.mk		# add CI/CD settings and targets
else
  -include .env
  export
  include dev.mk		# add development settings and targets
endif

# SKAO Makefiles
# SRCNet shared settings and targets via srcnet.mk:
#   major-branch / minor-branch / patch-branch NAME=<name>
#                       - create a <type>-<name> release branch
#   push                - push the current branch to origin
#   bump-and-commit     - bump the release version based on the branch
#                         prefix and commit the bumped files (no-op on detached HEAD)
#   oci-pre-build       - overridden as a no-op; outside CI, OCI_SKIP_PUSH=true
#   oci-pre-build-all   - CI only, opt in with SRC_CHECK_BEHIND_MAIN=yes:
#                         fail the build if the branch is behind origin/main
include .make/srcnet.mk
include .make/base.mk
include .make/helm.mk
include .make/oci.mk
include .make/k8s.mk
include .make/python-uv.mk

# Lockfiles: uv.lock (server, pyproject.toml) and uv.client.lock (client, pyproject.client.toml).
# Extra uv flags via UV_LOCK_ARGS, e.g. make lock UV_LOCK_ARGS=--upgrade
UV_LOCK_ARGS ?=

.PHONY: lock lock-server lock-client lock-check \
	client-bump-patch-release client-bump-minor-release client-bump-major-release

lock: lock-server lock-client  ## update both uv.lock and uv.client.lock

lock-server:  ## update uv.lock from pyproject.toml
	uv lock $(UV_LOCK_ARGS)

# uv cannot name its lockfile, so resolve the client in a scratch project dir.
lock-client:  ## update uv.client.lock from pyproject.client.toml
	@tmp=$$(mktemp -d) && trap 'rm -rf "$$tmp"' EXIT && \
	cp pyproject.client.toml "$$tmp/pyproject.toml" && \
	if [ -f uv.client.lock ]; then cp uv.client.lock "$$tmp/uv.lock"; fi && \
	uv lock --project "$$tmp" $(UV_LOCK_ARGS) && \
	cp "$$tmp/uv.lock" uv.client.lock

lock-check:  ## fail if uv.lock or uv.client.lock is out of date
	@$(MAKE) --no-print-directory lock-server lock-client UV_LOCK_ARGS=--locked

# release.mk set-release would also bump pyproject.toml/Chart.yaml, so the client bumps are bespoke.
# Plain `make` (not $(MAKE)) so CI's `make -n` target check only prints this recipe.
client-bump-patch-release: CLIENT_NEXT_LEVEL := nextPatchLevel
client-bump-minor-release: CLIENT_NEXT_LEVEL := nextMinorLevel
client-bump-major-release: CLIENT_NEXT_LEVEL := nextMajorLevel
client-bump-patch-release client-bump-minor-release client-bump-major-release:
	@. $(RELEASE_SUPPORT); CONFIG=client setReleaseFile; \
	version=$$($(CLIENT_NEXT_LEVEL)); \
	if tagExists "client-$$version"; then echo "ERROR: tag client-$$version already exists" >&2; exit 1; fi; \
	bk=$$(mktemp -d) || exit 1; \
	cp .release_client pyproject.client.toml uv.client.lock "$$bk"/ || { rm -rf "$$bk"; exit 1; }; \
	new=$$(mktemp pyproject.client.toml.XXXXXX) || { rm -rf "$$bk"; exit 1; }; \
	if ! { printf 'release=%s\ntag=client-%s\n' "$$version" "$$version" > .release_client && \
		sed -E "s|^(version[[:space:]]*=[[:space:]]*\")([^\"]*)(\")|\1$${version}\3|" pyproject.client.toml > "$$new" && \
		mv -f "$$new" pyproject.client.toml && \
		make --no-print-directory lock-client; }; then \
		cp "$$bk"/.release_client "$$bk"/pyproject.client.toml "$$bk"/uv.client.lock .; rm -rf "$$bk" "$$new"; \
		echo "ERROR: client bump to $$version failed; version files restored" >&2; exit 1; \
	fi; \
	rm -rf "$$bk"; \
	echo "Client version bumped to $$version (tag client-$$version)"

ifneq ($(CI_JOB_ID),)
# Swap in pyproject.client.toml / uv.client.lock for client builds.
PYPROJECT_VARIANT ?= server

python-pre-lint python-pre-build python-pre-test python-pre-publish: python-variant-swap

python-variant-swap:
ifeq ($(PYPROJECT_VARIANT),client)
	cp pyproject.client.toml pyproject.toml
	cp uv.client.lock uv.lock
endif

# Tag builds must match the variant's pyproject version: <X.Y.Z> (server) or client-<X.Y.Z> (client).
ifneq ($(CI_COMMIT_TAG),)
python-pre-build: python-check-tag-version

python-check-tag-version: python-variant-swap
	@version=$$(uv version --short); \
	expected=$$([ "$(PYPROJECT_VARIANT)" = client ] && echo "client-$$version" || echo "$$version"); \
	if [ "$$expected" != "$(CI_COMMIT_TAG)" ]; then \
		echo "Tag $(CI_COMMIT_TAG) does not match $(PYPROJECT_VARIANT) version $$version (expected tag $$expected)"; \
		exit 1; \
	fi
endif
endif

# Defined after the includes so it doesn't become the default goal.
# Run explicitly with: make contributors
.PHONY: contributors
contributors:
	@python3 tools/generate_contributors.py > CONTRIBUTORS.md