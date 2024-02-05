# SKA SRC Site Capabilities API

This API exposes enables functionality related to SRCNet site service discovery and management.

[TOC]

## Authentication

### User

To access this API as a user, the user needs to have first authenticated with the SRCNet and to have exchanged the token 
resulting from this initial authentication with one that allows access to this specific service. See the Authentication 
Mechanism and Token Exchange Mechanism sections of the Authentication API for more specifics.

### Service

For service-to-service interactions, it is possible to obtain a token via a ***client_credentials*** grant to the 
ska-src-site-capabilities-api IAM client.

## Authorisation

Hereafter, the caller (either a user or another service) is assumed to have a valid token allowing access to this API. 
Authenticated requests are then made by including this token in the header.

The token audience must also match the expected audience, also defined in the site-capabilities-api permissions policy 
(default: “site-capabilities-api”).

### Restricting user access to routes using token scopes

The presented token must include a specific scope expected by the service to be permitted access to all API routes. This 
scope is defined in the site-capabilities-api permissions policy (default: “site-capabilities-api-service”). 

**This scope must also be added to the IAM permissions client otherwise the process of token instrospection will drop 
this scope.**

### Restricting user access to routes using IAM groups

Access to a specific route of this API depends on user IAM group membership and is determined by calls to the 
`/authorise/route` path of the Permissions API. Groups are typically nested with the pattern 
`root_group/roles/site/role` for site specific permissions or `root_group/roles/role` for global permissions.

As an example, consider get/set site services functionality. For specific site permissions for the site "SKAOSRC", the 
required group hierarchy may look something like:

```
/services/site-capabilities-api/
   roles/SKAOSRC/
      viewer
      manager
```

where the `/sites/{site}` get route is protected by the following permission policy mapping API routes to "roles":

```json
{
   "/sites/{site}": {
      "GET": "site-viewer or site-manager",
      "DELETE": "site-manager"
   },
}
```

and the roles `site-viewer` and `site-manager` are only assigned for users who have the following IAM group membership:

```json
{
   "site-viewer": [
      "{root_group}/roles/{site}/viewer"
    ],
   "site-manager": [
      "{root_group}/roles/{site}/manager"
   ],
}
```

## Operations

Operations are grouped into the follow sections:

| <div style="width:160px">Group</div> | Description                                  |
|:-------------------------------------|:---------------------------------------------|
| Sites                                | Operations on sites.                         |
| Compute                              | Operations on processing offered by sites    |
| Storages                             | Operations on storages offered by sites      |
| Storage Areas                        | Operations on storage areas offered by sites |
| Services                             | Operations on services offered by sites      |
| Schemas                              | Schema operations.                           |
| Status                               | Operations describing the status of the API. |

## Schemas

It is recommended to record data in the document database by using the web frontend (`/www/sites/add`). This form 
verifies the input against the site schema at `etc/schemas/site.json` (which is, as an aside, constructed using 
other schemas in the same directory by referencing). For each record created or modified, a version number is 
incremented for the corresponding site and the input stored alongside the schema used to generate the form. All 
versions of a site specification are retained. Sites can be added programmatically, but care should be taken to keep 
the input in line with the corresponding schema.

Schemas are flexible and new ones can be added/existing ones amended.

### Adding and amending schemas

To amend/add a new resource, the following checklist may be helpful:

- (adding only) Create the schema and add to the `etc/schemas` directory
- Add to or amend any models (`src/ska_src_site_capabilities_api/models`) if there are new ones or the schema of an 
  existing model has changed
- Amend the site template (`src/ska_src_site_capabilities_api/rest/templates/site.html`):
    - Add any new fields to the form schema
    - Ensure that if there are object fields that a default `value` of `[]` is set using the jinja2 template `| default` 
    filter
- Amend the REST server (`src/ska_src_site_capabilities_api/rest/server.py`):
    - Add any routes and corresponding backend functions (check that existing functionality isn't broken with any big
      changes!)
    - Add a new tag to the `openapi_schema` (if a new section for routes has been defined)
    - Change `responses` in the `app` route decorator to reference the appropriate models
- (optional) Check that the `etc/init/sites.json` has entries that conform to the new schema

In addition you will need to amend external dependencies by:

- Ensuring that any dependent calls that utilise this schema aren't adversely, and 
- If a new route has been created or its signature modified, check that the corresponding Permissions API policy has 
  been added/amended

## Development

Makefile targets have been included to facilitate easier and more consistent development against this API. The general 
recipe is as follows:

1. Depending on the fix type, create a new major/minor/patch branch, e.g. 
    ```bash
    $ make patch-branch NAME=some-name
    ```
    Note that this both creates and checkouts the branch.
2. Make your changes.
3. Create new code samples if necessary.
   ```bash
   $ make code-samples
   ```
4. Add your changes to the branch:
    ```bash
   $ git add ...
    ```
5. Either commit the changes manually (if no version increment is needed) or bump the version and commit, entering a 
   commit message when prompted:
    ```bash
   $ make bump-and-commit
    ```
6. Push the changes upstream when ready:
    ```bash
   $ make push
    ```

Note that the CI pipeline will fail if python packages with the same semantic version are committed to the GitLab 
Package Registry.

### Bypassing AuthN/Z

AuthN/Z can be bypassed for development by setting `DISABLE_AUTHENTICATION=yes` in the environment.

## Deployment

Deployment is managed by docker-compose or helm.

The docker-compose file can be used to bring up the necessary services locally i.e. the REST API, setting the mandatory
environment variables. Sensitive environment variables, including those relating to the IAM client, should be kept in
`.env` files to avoid committing them to the repository.

There is also a helm chart for deployment onto a k8s cluster.

### Example via docker-compose

Edit the `.env.template` file accordingly and rename to `.env`, then:

```bash
eng@ubuntu:~/SKAO/ska-src-site-capabilities-api$ docker-compose up
```

### Example via Helm

After editing the `values.yaml` (template in `/etc/helm/`):

```bash
$ create namespace ska-src-site-capabilities-api
$ helm install --namespace ska-src-site-capabilities-api ska-src-site-capabilities-api .
```

## Prototype

A prototype of this service is deployed at site-capabilities.srcdev.skao.int/api. This prototype application 
uses the SKA IAM client ska-src-site-capabilities-api.

## References

1. https://gitlab.com/ska-telescope/src/src-service-apis/ska-src-site-capabilities-api
