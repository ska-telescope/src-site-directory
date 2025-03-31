CLUSTER_DOMAIN=cluster.local

## Chart configuration for deployment in dev context (k8s.mk)
K8S_CHART_PARAMS += \
	--set svc.api.image.image=$(PROJECT_NAME) \
	--set svc.api.image.pullPolicy=Never \
	--set svc.api.image.tag=$(VERSION) \
	--set persistence.storageClass=standard

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

# Override pre for k8s-install-chart (k8s.mk): load the deployment image into minikube first
k8s-pre-install-chart: oci-build
	minikube image load $(CAR_OCI_REGISTRY_HOST)/$(NAME):$(VERSION)

# Override post for k8s-test (k8s.mk): remove the generated requirements file
k8s-post-test:
	rm tests/requirements.txt

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

# Override pre for oci-build (oci.mk): skip pushing the image to the registry as only used in minikube context
oci-pre-build:
	export OCI_SKIP_PUSH=true

patch-branch:
	@test -n "$(NAME)"
	@echo "making patch branch \"$(NAME)\""
	@git branch patch-$(NAME)
	@git checkout patch-$(NAME)

push:
	@git push origin `git branch --show-current`
