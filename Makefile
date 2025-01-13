.PHONY: docs

CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-src-site-capabilities-api
KUBE_APP = ska-src-site-capabilities-api
KUBE_NAMESPACE ?= ska-src-site-capabilities-api

FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest
MARK ?= unit_test
ADDMARK ?= # additional markers
PYTHON_TEST_COUNT ?= 1

ifeq ($(MAKECMDGOALS),python-test)
ADD_ARGS +=  --forked --count=$(PYTHON_TEST_COUNT)
MARK = not post_deployment $(ADDMARK)
endif
ifeq ($(MAKECMDGOALS),k8s-test)
ADD_ARGS +=  --true-context --count=$(COUNT)
MARK = post_deployment
endif

ifeq ($(EXIT_AT_FAIL),true)
ADD_ARGS += -x
endif

IAM_CLIENT_SECRET ?=
MONGO_PASSWORD ?=

# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= test
HELM_CHARTS_TO_PUBLISH=

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART=ska-src-site-capabilities-api
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
K8S_CHARTS ?= ska-src-site-capabilities-api ## list of charts
K8S_CHART ?= $(HELM_CHART)


CI_REGISTRY ?= gitlab.com

CUSTOM_VALUES = --set site_capabilities_api.image.tag=$(VERSION) \
--set svc.secrets.credentials.iam_client_secret=$(IAM_CLIENT_SECRET) \
--set svc.secrets.credentials.mongo_password=$(MONGO_PASSWORD)

K8S_TEST_IMAGE_TO_TEST=$(CAR_OCI_REGISTRY_HOST)/$(PROJECT):$(VERSION)

ifneq ($(CI_JOB_ID),)
CUSTOM_VALUES = --set site_capabilities_api.image.image=$(PROJECT) \
	--set site_capabilities_api.image.registry=$(CI_REGISTRY)/ska-telescope/src/src-service-apis/$(PROJECT) \
	--set site_capabilities_api.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA) \
	--set svc.secrets.credentials.iam_client_secret=$(IAM_CLIENT_SECRET)\
	--set svc.secrets.credentials.mongo_password=$(MONGO_PASSWORD)
K8S_TEST_IMAGE_TO_TEST=$(CI_REGISTRY)/ska-telescope/src/src-service-apis/$(PROJECT)/$(PROJECT):$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
endif

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)


PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE)

K8S_CHART_PARAMS = $(CUSTOM_VALUES)

K8S_TEST_TEST_COMMAND = $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
						pytest \
						$(PYTHON_VARS_AFTER_PYTEST) ./tests \
						| tee pytest.stdout

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

-include .make/python.mk
-include .make/base.mk
-include .make/oci.mk
-include .make/helm.mk
-include .make/k8s.mk
-include PrivateRules.mak


test-requirements:
	@poetry export --without-hashes --with dev --format requirements.txt --output tests/requirements.txt

k8s-pre-test: python-pre-test test-requirements

requirements: ## Install Dependencies
	poetry install

cred:
	make k8s-namespace
	make k8s-namespace-credentials

