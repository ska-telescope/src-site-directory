# Set build context as PWD for multiple images
OCI_IMAGE_BUILD_CONTEXT = $(PWD)

CURRENT_COMMIT_HASH=$(git rev-parse HEAD)
LAST_COMMIT_HASH=$(git log -n 1)

echo $(CURRENT_COMMIT_HASH)
echo $(LAST_COMMIT_HASH)

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
include .make/base.mk
include .make/helm.mk
include .make/k8s.mk
include .make/oci.mk
include .make/python.mk