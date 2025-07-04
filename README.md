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

## Schemas

It is recommended to record data in the document database by using the web frontend
(`/www/nodes/`, `/www/nodes/<node_name>`). These forms perform both client and server side verification of the input 
against the node schema at `etc/schemas/node.json` (which is, as an aside, constructed using 
other schemas in the same directory by referencing). For each record created or modified, a version number is 
incremented for the corresponding node and the input stored alongside the schema used to generate the form. All 
versions of a node specification are retained. Nodes can be added programmatically, but care should be taken to keep 
the input in line with the corresponding schema.

Schemas are flexible and new ones can be added/existing ones amended.

### Adding and amending schemas

To amend/add a new resource, the following checklist may be helpful:

- (adding only) Create the schema and add to the `etc/schemas` directory
- (amending only) Edit the corresponding schema in the `etc/schemas` directory
- Add to or amend any models (`src/ska_src_site_capabilities_api/models`) if there are new ones or the schema of an 
  existing model has changed
- Amend the form uis (`src/ska_src_site_capabilities_api/rest/static/js/add-node-form-ui.js`, `src/ska_src_site_capabilities_api/rest/static/js/edit-node-form-ui.js`)
- Amend the node template (`src/ska_src_site_capabilities_api/rest/templates/node.html`):
- Amend the REST server (`src/ska_src_site_capabilities_api/rest/server.py`):
    - Add any routes and corresponding backend functions (check that existing functionality isn't broken with any big
      changes!)
    - Add a new tag to the `openapi_schema` (if a new section for routes has been defined)
    - Change `responses` in the `app` route decorator to reference the appropriate models
- (optional) Check that the `etc/init/nodes.json` has entries that conform to the new schema

In addition you will need to amend external dependencies by:

- Ensuring that any dependent calls that utilise this schema aren't adversely affected, and 
- If a new route has been created or its signature modified, check that the corresponding Permissions API policy has 
  been added/amended

## Deployment

Deployment is managed by docker-compose or helm.

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