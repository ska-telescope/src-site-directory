# Bespoke chart configuration for deployment in CI/CD context (k8s.mk)
K8S_CHART_PARAMS += \
	--set svc.api.image.image=$(PROJECT) \
	--set svc.api.image.registry=registry.gitlab.com/ska-telescope/src/src-service-apis/$(PROJECT) \
	--set svc.api.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA) \
	--set persistence.storageClass=bds1