# Configuration items for python linting and formatting targets (python.mk)
PYTHON_LINE_LENGTH=120
PYTHON_SWITCHES_FOR_ISORT=
PYTHON_SWITCHES_FOR_BLACK=
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=F401,F811,F821,W503
PYTHON_SWITCHES_FOR_PYLINT=--ignore=W503

# Configuration items for k8s deployment testing (k8s.mk)
PROJECT=ska-src-site-capabilities-api
K8S_TEST_RUNNER=test-runner-$(HELM_RELEASE)
K8S_TEST_IMAGE_TO_TEST=python:3.8-slim-buster	# the image used by the test runner inside the deployment environment

# Common configuration items for pytest (python.mk, k8s.mk)
# The following sets the expected location of the package inside CI & sets the required variables for component testing.
PYTHON_VARS_BEFORE_PYTEST=PYTHONPATH=.:./src CLUSTER_DOMAIN=$(CLUSTER_DOMAIN) KUBE_NAMESPACE=$(KUBE_NAMESPACE) DISABLE_AUTHENTICATION=$(DISABLE_AUTHENTICATION)
ifeq ($(MAKECMDGOALS),python-test)					# if running pytest outside of deployment test runner
    PYTHON_VARS_AFTER_PYTEST=-x -m 'not post_deployment' $(FILE)
endif
ifeq ($(MAKECMDGOALS),k8s-test)						# if running pytest inside deployment test runner
    PYTHON_VARS_AFTER_PYTEST=-x -m 'post_deployment' $(FILE)
endif

# Override pre for k8s-test (k8s.mk): create requirements.txt in required place to be passed in to test runner (/tests)
k8s-pre-test:
	@poetry export --without-hashes --with dev --format requirements.txt --output tests/requirements.txt

# Common chart configuration for deployment in any context (k8s.mk)
K8S_CHART_COMMON_PARAMS = \
	--set secrets.api.iam_client.id=$(API_IAM_CLIENT_ID) \
	--set secrets.api.iam_client.secret=$(API_IAM_CLIENT_SECRET) \
	--set secrets.api.sessions.key=$(SESSIONS_SECRET_KEY) \
	--set secrets.common.mongo.password=$(MONGO_PASSWORD) \
	--set ing.enabled=false \
	--set svc.api.mongo_host=mongo.$(KUBE_NAMESPACE).svc.$(CLUSTER_DOMAIN)
