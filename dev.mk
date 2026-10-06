CLUSTER_DOMAIN=cluster.local

## Bespoke chart configuration for deployment in dev context (k8s.mk)
K8S_CHART_PARAMS += $(K8S_CHART_COMMON_PARAMS) \
	--set svc.api.image.image=$(PROJECT)-core \
	--set svc.api.image.pullPolicy=Never \
	--set svc.api.image.tag=$(VERSION) \
	--set persistence.storageClass=standard

# Override pre for k8s-install-chart (k8s.mk): load the deployment image into minikube first
k8s-pre-install-chart: oci-build
	minikube image load $(CAR_OCI_REGISTRY_HOST)/$(NAME):$(VERSION)

# Override post for k8s-test (k8s.mk): remove the generated requirements file
k8s-post-test:
	rm tests/requirements.txt

k8s-test-auth:
	@echo "Running tests with authentication ENABLED..."
	@make k8s-install-chart K8S_CHART_PARAMS="$(K8S_CHART_PARAMS) --set svc.api.disable_authentication=no"
	# can't just override PYTHON_VARS_BEFORE_PYTEST as this will already have been evaluated in the assignment of
    # K8S_TEST_TEST_COMMAND, which is the command ran directly in the test runner, so have to amend command directly.
	@K8S_TEST_TEST_COMMAND=$$(echo "$$K8S_TEST_TEST_COMMAND" | sed 's/DISABLE_AUTHENTICATION=[^ ]*/DISABLE_AUTHENTICATION=no/') && export K8S_TEST_TEST_COMMAND && make k8s-test

k8s-test-noauth:
	@echo "Running tests with authentication DISABLED..."
	@make k8s-install-chart K8S_CHART_PARAMS="$(K8S_CHART_PARAMS) --set svc.api.disable_authentication=yes"
	# can't just override PYTHON_VARS_BEFORE_PYTEST as this will already have been evaluated in the assignment of
    # K8S_TEST_TEST_COMMAND, which is the command ran directly in the test runner, so have to amend command directly.
	@K8S_TEST_TEST_COMMAND=$$(echo "$$K8S_TEST_TEST_COMMAND" | sed 's/DISABLE_AUTHENTICATION=[^ ]*/DISABLE_AUTHENTICATION=yes/') && export K8S_TEST_TEST_COMMAND && make k8s-test

