# SKA SRC Site Capabilities API

[[_TOC_]]

## Overview

This API exposes enables functionality related to SRCNet site service discovery and management.

## Structure

The repository is structured as follows:

```bash
.
├── .env.template
├── .gitlab-ci.yml
├── docker-compose.yml
├── Dockerfile
├── etc
│   ├── docker
│   │   └── init.sh
│   ├── helm
│   │   ├── Chart.yaml
│   │   ├── templates
│   │   └── values.yaml.template
│   ├── init
│   └── schemas
├── LICENSE
├── README.md
├── requirements.txt
├── setup.py
├── src
│   └── ska_src_site_capabilities_api
│       ├── client
│       ├── common
│       ├── db
│       └── rest
├── TODO.md
└── VERSION
```

## Authentication

To access this API a user needs to have first authenticated with the SRCNet and to have exchanged the token resulting 
from this initial authentication with one that allows access to this specific service. See the Authentication Mechanism 
and Token Exchange Mechanism sections of the Authentication API document for more specifics.

Hereafter, the user is assumed to have authenticated with the SRCNet and to have exchanged their token with one allowing 
access to this service. Authenticated requests are then made by including this token in the header.

## Authorisation

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
   ...
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
   ...
}
```

## Schemas

It is recommended to record data in the document database by using the web frontend (`/www/sites/add`). This form 
verifies the input against the site schema at `etc/schemas/site.json` (which is, as an aside, constructed using 
`storage.json` and `storage-access-protocol.json` schemas in the same directory by referencing). For each record created 
or modified, a version number is incremented for the corresponding site and the input stored alongside the schema used 
to generate the form. All versions of a site specification are retained.

New fields can be added to schemas, but you must remember to add the element on the form template too.

Sites can be added programmatically, but care should be taken to keep the input in line with the corresponding schema.

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

```
$ create namespace ska-src-site-capabilities-api
$ helm install --namespace ska-src-site-capabilities-api ska-src-site-capabilities-api .
```

