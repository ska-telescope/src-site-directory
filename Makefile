.PHONY: docs
FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest
MARK ?= unit_test
ADDMARK ?= # additional markers

PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE)

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
-include PrivateRules.mak
