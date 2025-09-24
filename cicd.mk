# Bespoke chart configuration for deployment in CI/CD context (k8s.mk)
K8S_CHART_PARAMS += $(K8S_CHART_COMMON_PARAMS) \
	--set svc.api.image.image=scapi-core \
	--set svc.api.image.registry=registry.gitlab.com/ska-telescope/src/src-service-apis/$(PROJECT) \
	--set svc.api.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA) \
	--set persistence.storageClass=bds1 \
	--set svc.api.disable_authentication=$(DISABLE_AUTHENTICATION) \
	--set svc.api.permissions_api_url=http://localhost \
	--set svc.api.auth_api_url=http://localhost

# Build additional tag for integration environment (oci.mk)
OCI_BUILD_ADDITIONAL_TAGS = $(CI_COMMIT_REF_SLUG)

oci-pre-build-all:
	@git fetch origin main;
	@echo "🚀 Checking branch HEAD..."
	@if ! git merge-base --is-ancestor origin/main HEAD; then \
        echo "❌ Branch is behind origin/main. Please rebase or merge main before proceeding."; \
        exit 1; \
    else \
        echo "🚀 ✅ Branch is up to date with origin/main. Building project..."; \
    fi