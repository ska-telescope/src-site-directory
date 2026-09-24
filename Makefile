# Set build context as PWD for multiple images
OCI_IMAGE_BUILD_CONTEXT = $(PWD)

# Build additional tag for integration environment (oci.mk)
OCI_BUILD_ADDITIONAL_TAGS = $(CI_COMMIT_REF_SLUG)

contributors:
	@python3 tools/generate_contributors.py > CONTRIBUTORS.md

# Bespoke partial Makefiles
include testing.mk		# add testing settings and targets
-include .env

# SKAO Makefiles
include .make/srcnet.mk
include .make/base.mk
include .make/helm.mk
include .make/k8s.mk
include .make/oci.mk
include .make/python.mk