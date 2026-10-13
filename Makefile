# Set build context as PWD for multiple images
OCI_IMAGE_BUILD_CONTEXT = $(PWD)

# Build additional tag for integration environment (oci.mk)
OCI_BUILD_ADDITIONAL_TAGS = $(CI_COMMIT_REF_SLUG)

# Docs are built with the 'docs' dependency group (docs.mk)
DOCS_PYTHON_RUNNER := uv run python3

docs-pre-build:
	uv sync --group docs

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

# Defined after the includes so it doesn't become the default goal.
# Run explicitly with: make contributors
.PHONY: contributors
contributors:
	@python3 tools/generate_contributors.py > CONTRIBUTORS.md