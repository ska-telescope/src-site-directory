# SRC Site Directory

This is a prototype system to record, store and programmatically expose attributes relating to sites within the SRCNet. Such attributes 
may relate to storage, compute, services etc.

![spinning globe](doc/globe.gif "spinning globe")

## Structure

The repository is structed as follows:

```bash
.
├── docker-compose.yml
├── Dockerfile
├── etc
│   ├── docker
│   ├── init
│   ├── helm
│   ├── permissions
│   ├── roles
│   └── schemas
├── README.md
├── requirements.txt
├── setup.py
└── src
    └── site_directory
```

### Deployment

Deployment is managed by docker or helm. 

There exists a `docker-compose` file to bring up the necessary services i.e. the REST API and the mongodb backend, 
a `Dockerfile` to build the api image and a `.env` to store sensitive credentials related to the IAM client used to 
provide AuthN/Z.

There is also a helm chart for deployment onto a k8s cluster.

### Authorisation

Authorisation is managed using the concepts of groups, roles and permissions. Groups are bound to roles and roles are 
bound to permissions. A permission is defined by a route and a HTTP method. For examples, see `etc/roles/default.json` 
and `/etc/permissions/default.json`. Note that subgroups within a group can be used to limit access further, e.g. the 
`/sites/{site}` endpoint is restricted to users in the corresponding `/roles/{site}/viewer` group. 

### Schemas

It is recommended to record data in the document database by using the web frontend (`/www/sites/add`). This form 
verifies the input against the site schema at `etc/schemas/site.json` (which is, as an aside, constructed using 
`storage.json` and `storage-access-protocol.json` schemas in the same directory by referencing). For each record created 
or modified, a version number is incremented for the corresponding site and the input stored alongside the schema used 
to generate the form. All versions of a site specification are retained.

New fields can be added to schemas but you must remember to add the element on the form template too.

Sites can be added programatically, but care should be taken to keep the input in line with the corresponding schema.

### The REST API

The API is constructed using FastAPI. Frontend pages are also served via FastAPI with templating.

## Example deployment

Edit the `.env.template` file accordingly and rename to `.env`, then:

```bash
eng@ubuntu:~/SKAO/ska-site-directory$ docker-compose up
```

Alternatively, if you want to test without AuthN/Z, then remove dependencies for the route in 
`etc/site_directory/rest/server.py`. 

As usual, if you want to develop with hot-reloading, add a volume mount to the `docker-compose` file. The api will 
restart on file changes.

