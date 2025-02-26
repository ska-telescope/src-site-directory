.PHONY: docs

-include .make/base.mk      # provides make help, required for CI build process
-include .make/oci.mk       # provides oci-* targets, required for CI build process
-include .make/python.mk    # provides python-* targets, required for CI build process
-include .make/release.mk   # provides version tooling

# Configuration for python-lint and python-format targets.
PYTHON_LINE_LENGTH=120
PYTHON_SWITCHES_FOR_ISORT=
PYTHON_SWITCHES_FOR_BLACK=
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=F401,F811,F821,W503
PYTHON_SWITCHES_FOR_PYLINT=--ignore=W503

# Configuration for .release
HELM_CHARTS_TO_PUBLISH=ska-src-site-capabilities-api

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
