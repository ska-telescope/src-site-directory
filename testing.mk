# Configuration items for k8s deployment testing (k8s.mk)
PROJECT=scapi
PROJECT_NAME=scapi-core
K8S_TEST_RUNNER=test-runner-$(HELM_RELEASE)
# The test runner installs the locked dependencies with uv sync and runs pytest via uv run (k8s.mk does this
# when uv.lock is present), so it needs an image with uv; pin Python to match the runtime image.
K8S_TEST_IMAGE_TO_TEST=artefact.skao.int/ska-build-python-ubuntu24:1.0.0-rc.1
K8S_TEST_RUNNER_ADD_ARGS=--env=UV_PYTHON=3.13

# send pyproject.toml and uv.lock so the test runner can install the locked dependencies
k8s_test_src_dir = pyproject.toml uv.lock $(PYTHON_SRC)

# Common configuration items for pytest (python-uv.mk)
# The following sets the expected location of the package inside CI & sets the required variables for component testing.
PYTHON_VARS_BEFORE_PYTEST=PYTHONPATH=.:./src CLUSTER_DOMAIN=$(CLUSTER_DOMAIN) KUBE_NAMESPACE=$(KUBE_NAMESPACE) DISABLE_AUTHENTICATION=$(DISABLE_AUTHENTICATION)
ifeq ($(MAKECMDGOALS),python-test)					# if running pytest outside of deployment test runner
    PYTHON_VARS_AFTER_PYTEST=-x -m 'unit' $(FILE)
endif
ifeq ($(MAKECMDGOALS),k8s-test)						# if running pytest inside deployment test runner
    PYTHON_VARS_AFTER_PYTEST= -m 'component' $(FILE)
endif

# Common chart configuration for deployment in any context (k8s.mk)
K8S_CHART_COMMON_PARAMS = \
	--set secrets.api.iam_client.id=$(API_IAM_CLIENT_ID) \
	--set secrets.api.iam_client.secret=$(API_IAM_CLIENT_SECRET) \
	--set secrets.api.sessions.key=$(SESSIONS_SECRET_KEY) \
	--set secrets.common.mongo.password=$(MONGO_PASSWORD) \
	--set ing.enabled=false \
	--set svc.api.mongo_host=mongo.$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN) \
	--set svc.api.mongo_init_data_relpath=tests/assets