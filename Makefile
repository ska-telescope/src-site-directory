.PHONY: docs
FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest
MARK ?= unit_test
ADDMARK ?= # additional markers

PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE)
IAM_CLIENT_SECRET ?=
MONGO_PASSWORD ?=
KUBE_NAMESPACE ?= ska-src-site-capabilities-api
HELM_RELEASE ?= ska-src-site-capabilities-api
CHART_PATH ?= ./etc/helm

CHART_PARAMS ?= --set secrets.credentials.iam_client_secret=$(IAM_CLIENT_SECRET)\
--set secrets.credentials.mongo_password=$(MONGO_PASSWORD)

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

helm-install:
	helm install $(HELM_RELEASE) \
	$(CHART_PARAMS) \
	$(CHART_PATH) --namespace $(KUBE_NAMESPACE)


-include .make/python.mk
-include .make/base.mk
-include .make/oci.mk
-include PrivateRules.mak
