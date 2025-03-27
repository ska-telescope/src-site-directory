# Global configuration variables
PROJECT=ska-src-site-capabilities-api

# SKAO Makefiles
-include .make/base.mk
-include .make/helm.mk
-include .make/k8s.mk
-include .make/oci.mk
-include .make/python.mk

# Bespoke Makefiles
-include testing.mk     	# add testing

ifneq ($(CI_JOB_ID),)
	-include cicd.mk        # add CI/CD
else
	-include dev.mk         # add development
endif

