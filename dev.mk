.PHONY: docs

## Bespoke chart configuration (k8s.mk)
K8S_CHART_PARAMS = \
	--set svc.api.image.tag=$(VERSION) \
	--set secrets.api.iam_client.id=$(IAM_CLIENT_ID) \
	--set secrets.api.iam_client.secret=$(IAM_CLIENT_SECRET) \
	--set secrets.api.sessions.key=$(SESSIONS_KEY) \
	--set secrets.common.mongo.password=$(MONGO_PASSWORD) \
K8S_TEST_IMAGE_TO_TEST ?= $(CAR_OCI_REGISTRY_HOST)/$(PROJECT):$(VERSION)

# Bumps a release according to the branch name (release.mk)
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
