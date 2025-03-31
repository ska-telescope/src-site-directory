# SKAO Makefiles
include .make/base.mk
include .make/helm.mk
include .make/k8s.mk
include .make/oci.mk
include .make/python.mk

# Bespoke Makefiles
include testing.mk		# add testing settings and targets
ifneq ($(CI_JOB_ID),)
  include cicd.mk		# add CI/CD settings and targets
else
  -include .env
  export
  include dev.mk		# add development settings and targets
endif

