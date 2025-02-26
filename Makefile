.PHONY: docs

-include .make/base.mk      # provides make help, required for CI build process, and version tooling
-include .make/oci.mk       # provides oci-* targets, required for CI build process
-include .make/python.mk    # provides python-* targets, required for CI build process

# Configuration for python linting and formatting targets (python.mk)
PYTHON_LINE_LENGTH=120
PYTHON_SWITCHES_FOR_ISORT=
PYTHON_SWITCHES_FOR_BLACK=
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=F401,F811,F821,W503
PYTHON_SWITCHES_FOR_PYLINT=--ignore=W503

# Configuration for release management targets (release.mk)
HELM_CHARTS_TO_PUBLISH=ska-src-site-capabilities-api

bump-and-commit:
	@bash -c ' \
		CURRENT_BRANCH=$$(git branch --show-current); \
		echo "Current branch: $$CURRENT_BRANCH"; \
		if echo "$$CURRENT_BRANCH" | grep -q "patch"; then \
			make bump-patch-release; \
		elif echo "$$CURRENT_BRANCH" | grep -q "minor"; then \
			make bump-minor-release; \
		elif echo "$$CURRENT_BRANCH" | grep -q "major"; then \
			make bump-major-release; \
		else \
			echo "Error: Current branch $$CURRENT_BRANCH is not a valid patch, minor, or major branch"; \
			exit 1; \
		fi; \
		git add .release etc/helm/Chart.yaml pyproject.toml; \
		git commit \
	'

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
	@git push origin `git branch --show-current`
