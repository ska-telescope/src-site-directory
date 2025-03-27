-include testing.mk

# Bespoke configuration items for k8s deployment testing (k8s.mk)
K8S_TEST_RUNNER=test-runner-$(HELM_RELEASE)

# Bespoke configuration items for pytest (python.mk, k8s.mk)
PYTHON_VARS_BEFORE_PYTEST=PYTHONPATH=.:./src        # expected location of package inside CI test runner
ifeq ($(MAKECMDGOALS),python-test)					# if running pytest outside of test runner
    PYTHON_VARS_AFTER_PYTEST=-x -m 'not post_deployment' $(FILE)
endif
ifeq ($(MAKECMDGOALS),k8s-test)						# if running pytest inside test runner
    PYTHON_VARS_AFTER_PYTEST=-x -m 'post_deployment' $(FILE)
endif

# Bespoke chart configuration (k8s.mk)
K8S_CHART_PARAMS = \
	--set svc.api.image.image=$(PROJECT) \
	--set svc.api.image.registry=registry.gitlab.com/ska-telescope/src/src-service-apis/$(PROJECT) \
	--set svc.api.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA) \
	--set secrets.api.iam_client.id=$(IAM_CLIENT_ID) \
	--set secrets.api.iam_client.secret=$(IAM_CLIENT_SECRET) \
	--set secrets.api.sessions.key=$(SESSIONS_KEY) \
	--set secrets.common.mongo.password=$(MONGO_PASSWORD) \
	--set persistence.storageClass=bds1 \
	--set ing.enabled=false
K8S_TEST_IMAGE_TO_TEST = python:3.8-bullseye

# Override pre for k8s-test: create requirements.txt in required place to be passed in to test runner (/tests)
k8s-pre-test:
	@poetry export --without-hashes --with dev --format requirements.txt --output tests/requirements.txt

