# SKA SRC Site Capabilities API

This API exposes functionality related to SRCNet site storage/service discovery and management.

[TOC]

## Overview

The Site Capabilities API enables the following functionality by group:

| <div style="width:160px">Group</div> | Description                                  |
|:-------------------------------------|:---------------------------------------------|
| Nodes                                | Operations on nodes.                         |
| Sites                                | Operations on sites.                         |
| Compute                              | Operations on processing offered by sites    |
| Storages                             | Operations on storages offered by sites      |
| Storage Areas                        | Operations on storage areas offered by sites |
| Services                             | Operations on services offered by sites      |
| Schemas                              | Schema operations.                           |
| Status                               | Operations describing the status of the API. |

## Python package installation

Choose one distribution for this API in each Python environment:

- `ska-src-site-capabilities-api`: the server package, which also includes the Python client. Use its bundled client when the server is installed.
- `ska-src-site-capabilities-api-client`: the standalone client package for applications that only need to call the API, without installing the server.

**Do not install both distributions in the same Python environment.** Both ship
`ska_src_site_capabilities_api/client`, so their client files overlap rather than
being independently owned. Installing or upgrading either can overwrite the
other's client code. Uninstalling either can remove shared files and break client
imports for the distribution that remains installed. Matching version numbers
does not remove this risk. The server's bundled client follows the server release;
it must not be upgraded separately using the standalone client package.

If both distributions have been installed, recreate the environment with only the
chosen distribution. When switching between server and client-only installations,
use a fresh virtual environment or container image rather than uninstalling just
one package and relying on the remaining installation. Check direct and transitive
dependencies so that they do not introduce both distributions for this API.

## AuthN/Z

### Authentication

#### User

To access this API as a user, the user needs to have first authenticated with the SRCNet and to have exchanged the token 
resulting from this initial authentication with one that allows access to this specific service. See the Authentication 
Mechanism and Token Exchange Mechanism sections of the Auth API for more specifics.

#### Service

For service-to-service interactions, it is possible to obtain a token via a ***client_credentials*** grant to the 
ska-src-site-capabilities-api IAM client.

### Authorisation

Hereafter, the caller (either a user or another service) is assumed to have a valid token allowing access to this API. 
Authenticated requests are then made by including this token in the header.

The token audience must also match the expected audience, also defined in the site-capabilities-api permissions policy 
(default: “site-capabilities-api”).

#### Restricting user access to routes using token scopes

The presented token must include a specific scope expected by the service to be permitted access to all API routes. This 
scope is defined in the site-capabilities-api permissions policy (default: “site-capabilities-api-service”). 

**This scope must also be added to the IAM permissions client otherwise the process of token introspection will drop 
this scope.**

#### Restricting user access to routes using IAM groups

Access to a specific route of this API depends on user IAM group membership and is determined by calls to the 
`/authorise/route` path of the Permissions API. Groups are typically nested with the pattern 
`root_group/roles/node/role` for node specific permissions or `root_group/roles/role` for global permissions.

As an example, consider get/set node services functionality. For specific node permissions for the node "SKAOSRC", the 
required group hierarchy may look something like:

```
/services/site-capabilities-api/
   roles/SKAOSRC/
      viewer
      manager
```

where the `/nodes/{node}` get route is protected by the following permission policy mapping API routes to "roles":

```json
{
   "/nodes/{node}": {
      "GET": "node-viewer or node-manager",
      "DELETE": "node-manager"
   },
}
```

and the roles `node-viewer` and `node-manager` are only assigned for users who have the following IAM group membership:

```json
{
   "node-viewer": [
      "{root_group}/roles/{node}/viewer"
    ],
   "node-manager": [
      "{root_group}/roles/{node}/manager"
   ],
}
```

Roles are assigned when a request to a particular endpoint is made. This enables information from the request to be used 
to understand if a role can be assigned. For example, consider the `node-viewer` role:

```
    "node-viewer": [
        "{root_group}/roles/{node}/viewer"
    ],
```

which requires both `root_group` and `node` to be provided. The `root_group` is an application specific parameter, 
but the `node` parameter is substituted when the request is made. In the case of a GET request for metadata, the 
route ```/nodes/{node}``` provides the `node` as a path parameter, and this value is substituted 
into the role definition. The source of the substitution for the role definition depends on either the path parameters, 
query parameters or body of the request; which are used depends on where the parameters are expected to come from.

## Deployment

Deployment is managed by docker-compose or helm.

For server deployments, retain the client bundled with the server package; do not
add `ska-src-site-capabilities-api-client` to the same container's Python environment,
including through application dependencies or runtime installation scripts. Client-only
applications can use the standalone client in a separate environment or container
and call the deployed server over HTTP. See [Python package installation](#python-package-installation)
for the shared-file risk and recovery guidance.

The docker-compose file can be used to bring up the necessary services locally i.e. the REST API, setting the mandatory
environment variables. Sensitive environment variables, including those relating to the IAM client, should be kept in
`.env` files to avoid committing them to the repository.

There is also a helm chart for deployment onto a k8s cluster.

### Example via docker-compose

Edit the `.env.template` file accordingly and rename to `.env`, then:

```bash
ska-src-site-capabilities-api$ docker-compose up
```

### Example via Helm

First build the docker image locally:

```bash
ska-src-site-capabilities-api$ make oci-image-build
```

Then install the chart (assumes Minikube):

```bash
ska-src-site-capabilities-api$ make k8s-install-chart
```