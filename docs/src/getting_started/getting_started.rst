===============
Getting started
===============

This page contains instructions for software developers who want to get
started with usage and development of the SKA SRC Site Capabilities repository.

Background
----------
Detailed information on how the SKA Software development
community works is available at the `SKA software developer portal <https://developer.skao.int/en/latest/>`_.
There you will find guidelines, policies, standards and a range of other
documentation.

Set up your development environment
-----------------------------------
This project is structured in a way that the test environment and test results are all completely reproducible and are independent of host environment. It uses ``make`` to provide a consistent UI (run ``make help`` for targets documentation).

How to Use
^^^^^^^^^^

Clone this repository:
::
>>> git clone https://gitlab.com/ska-telescope/src/src-service-apis/ska-src-site-capabilities-api.git
>>> cd ska-src-site-capabilities-api

Create and activate poetry environment:
::
>>> $ poetry shell

Install dependencies
::
>>> $ poetry install

Formatting the code:
::
>>> $ make python-format
[...]
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

Python linting:
::
>>> $ make python-lint
[...]
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)