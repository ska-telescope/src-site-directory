.PHONY: docs

CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-src-site-capabilities-api
KUBE_NAMESPACE ?= ska-src-site-capabilities-api

FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest
MARK ?= unit_test
ADDMARK ?= # additional markers

IAM_CLIENT_SECRET ?=
MONGO_PASSWORD ?=

# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= ska-src-site-capabilities-api
HELM_CHARTS_TO_PUBLISH=

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART=ska-src-site-capabilities-api
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
# UMBRELLA_CHART_PATH ?= ./etc/helm
K8S_CHARTS ?= ska-src-site-capabilities-api ## list of charts
K8S_CHART ?= $(HELM_CHART)


CI_REGISTRY ?= gitlab.com

K8S_CHART_PARAMS = --set site_capabilities_api.image.tag=$(VERSION) \
--set svc.secrets.credentials.iam_client_secret=$(IAM_CLIENT_SECRET) \
--set svc.secrets.credentials.mongo_password=$(MONGO_PASSWORD)

K8S_TEST_IMAGE_TO_TEST=$(CAR_OCI_REGISTRY_HOST)/$(PROJECT):$(VERSION)

ifneq ($(CI_JOB_ID),)
K8S_CHART_PARAMS = --set site_capabilities_api.image.image=$(PROJECT) \
	--set site_capabilities_api.image.registry=$(CAR_OCI_REGISTRY_HOST) \
	--set site_capabilities_api.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA) \
	--set svc.secrets.credentials.iam_client_secret=$(IAM_CLIENT_SECRET)\
	--set svc.secrets.credentials.mongo_password=$(MONGO_PASSWORD)
K8S_TEST_IMAGE_TO_TEST=$(CAR_OCI_REGISTRY_HOST)/$(PROJECT):$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
endif

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)


PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE)



# HELM_RELEASE ?= ska-src-site-capabilities-api
# CHART_PATH ?= ./etc/helm

# CHART_PARAMS ?= --set secrets.credentials.iam_client_secret=$(IAM_CLIENT_SECRET)\
# --set secrets.credentials.mongo_password=$(MONGO_PASSWORD)

bump-and-commit: 
	@cd etc/scripts && bash increment-app-version.sh `git branch | grep "*" | awk -F'[*-]' '{ print $$2 }' | tr -d ' '`
	@git add VERSION etc/helm/Chart.yaml
	@git commit

code-samples:
	@cd etc/scripts && bash generate-code-samples.sh

docs:
	@cd docs && make clean && make html

major-branch:
	@test -n "$(NAME)"
	@echo "making major branch \"$(NAME)\""
	@git branch major-$(NAME)
	@git checkout major-$(NAME)

minor-branch:
	@test -n "$(NAME)"
	@echo "making minor branch \"$(NAME)\""
	git branch minor-$(NAME)
	git checkout minor-$(NAME)

patch-branch:
	@test -n "$(NAME)"
	@echo "making patch branch \"$(NAME)\""
	@git branch patch-$(NAME)
	@git checkout patch-$(NAME)

push:
	@git push origin `git branch | grep "*" | awk -F'[*]' '{ print $$2 }' | tr -d ' '`

# helm-install:
# 	helm install $(HELM_RELEASE) \
# 	$(CHART_PARAMS) \
# 	$(CHART_PATH) --namespace $(KUBE_NAMESPACE)


-include .make/python.mk
-include .make/base.mk
-include .make/oci.mk
-include .make/helm.mk
-include .make/k8s.mk
-include PrivateRules.mak
