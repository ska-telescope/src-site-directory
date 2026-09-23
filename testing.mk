PYTHON_LINE_LENGTH=150
PYTHON_SWITCHES_FOR_ISORT=
PYTHON_SWITCHES_FOR_BLACK=
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=F401,F811,F821,W503
PYTHON_SWITCHES_FOR_PYLINT=--ignore=W503,W0212

# Common configuration items for pytest (python.mk, k8s.mk)
# The following sets the expected location of the package inside CI & sets the required variables for component testing.
PYTHON_VARS_BEFORE_PYTEST=PYTHONPATH=.:./src CLUSTER_DOMAIN=$(CLUSTER_DOMAIN) KUBE_NAMESPACE=$(KUBE_NAMESPACE) DISABLE_AUTHENTICATION=$(DISABLE_AUTHENTICATION)
ifeq ($(MAKECMDGOALS),python-test)					# if running pytest outside of deployment test runner
    PYTHON_VARS_AFTER_PYTEST=-x -m 'unit' $(FILE)
endif
ifeq ($(MAKECMDGOALS),k8s-test)						# if running pytest inside deployment test runner
    PYTHON_VARS_AFTER_PYTEST= -m 'component' $(FILE)
endif