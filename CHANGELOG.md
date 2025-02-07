All notable changes to this project will be documented in this file.


Added
-----
[0.3.49]
********
* Pipeline improvements

[0.3.50]
********
* Implementation of secrets for MONGO and IAM credentials.
* Updates in templates to utilise secrets as helm variables.
* Use of template repository for make targets to install and uninstall chart.
* Deployment setup to install site capabilities chart on stfc pipeline in unique namespace.
* Namespace based on each commit added - costomised namespace names according to commit message.
* Jobs to destroy the created namespace manually.
* Implementation of integration tests.
* Test-runner pod setup to execute newly implemented tests.
* Implementation of separate jobs with separate namespace w.r.t enabled and disabled authentication.
* Documentatio for readthedocs for the adapted approach
* Helm configuration changes for gitlab pipeline to release/publish the chart on CAR(Central Artifact Repository).


Fixed
-----
