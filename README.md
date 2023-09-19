# GDPR Integration Template

This repository contains a simple Flask application which can be modified,
deployed and integrated with the centralized
[GDPR automation workflow](https://github.com/canonical/gdpr-workflows). It also
contains the packaging metadata for creating a ROCK of the Flask application.
For more information on ROCKs, visit the
[rockcraft Github](https://github.com/canonical/rockcraft). The application can
be deployed using the
[Charmed Flask K8s Operator](https://charmhub.io/flask-k8s).

Note: This template is an initial skeleton and is still missing some key
functionalities as outlined in the [TODO](#todo) section below.

## Integration Interface

The Flask application is composed of three endpoints and one middleware:

- `/search` endpoint: This is a GET request endpoint which requires an `email`
  query parameter. It must return an array of dictionaries representing the
  records found for the given email.
- `/delete` endpoint: This is a DELETE request endpoint which requires an
  `email` query parameter. If successful, it returns a `204 No Content`
  response.
- `/health`: This is a GET request endpoint which can be used to verify that the
  server is up and running.
- `authenticate` middleware: This function runs before every request made to the
  `/search` and `/delete` endpoints. It checks for the presence of the `email`
  query parameter and a valid `Authorization` header. This includes verifying
  that:
  - The email extracted from the access token belongs to the GDPR automation
    workflow's service account.
  - The `audience` value extracted from the access token matches the name of
    your application.

To add your application-specific search and delete logic, you need to modify the
`search_by_email` and `delete_by_email` methods under the `helpers` directory.

## How to Deploy

The steps outlined below are based on the assumption that you are building the
ROCK with the latest LTS of Ubuntu. If you are using another version of Ubuntu
or another operating system, the process may be different.

The steps outlined below assume you have the following installed on your
machine:

- [Microk8](https://juju.is/docs/sdk/set-up-your-development-environment#heading--install-microk8s)
- [Juju](https://juju.is/docs/sdk/set-up-your-development-environment#heading--set-up-juju)

### Building the ROCK

#### Clone Repository

```bash
git clone git@github.com:canonical/gdpr-integration-template.git
cd gdpr-integration-template
```

#### Installing Prerequisites

```bash
sudo snap install rockcraft --edge --classic
sudo snap install docker
sudo snap install lxd
sudo snap install skopeo --edge --devmode
sudo microk8s enable registry
```

#### Configuring Prerequisites

```bash
sudo usermod -aG docker $USER
sudo lxd init --auto
```

_NOTE_: You will need to open a new shell for the group change to take effect
(i.e. `su - $USER`)

#### Packing the Rock and Pushing to Local Registry

```bash
rockcraft pack
sudo skopeo --insecure-policy copy oci-archive:gdpr-flask_1.0_amd64.rock docker-daemon:localhost:32000/gdpr_flask:1.0

docker images | grep gdpr_flask # Note the image ID
docker tag <IMAGE_ID> localhost:32000/gdpr_flask:1.0
docker push localhost:32000/gdpr_flask

# Test that the image has been pushed correctly
docker pull localhost:32000/gdpr_flask
```

### Deploying the Charm

Create a new model using the following command:

```bash
juju add-model flask-tutorial
```

Deploy the flask-k8s charm using the following command:

```bash
juju deploy flask-k8s --channel edge --resource flask-app-image=localhost:32000/gdpr_flask
```

To monitor your deployment progress across various stages, use this command:

```bash
juju status --color --watch 2s
```

At this point, you can access your Flask application at `http://<UNIT_IP>:8000`.
You can use the `/health` endpoint to verify that the server is up and running.

## Connecting to GDPR Automation Workflow

To connect your application to the centralized
[GDPR automation workflow](https://github.com/canonical/gdpr-workflows), file a
[support request](https://warthogs.atlassian.net/secure/CreateIssue.jspa?issuetype=10799&pid=10113)
with the Commercial Systems team and provide the following:

- Application name (this must the value set in the `GDPR_AUDIENCE` environment
  variable)
- Contact
- Base URL
- Search Endpoint (Default: `/search`)
- Delete Endpoint (Default: `/delete`)

# TODO

- Outline steps to integrate with the
  [Nginx Ingress Integrator](https://charmhub.io/nginx-ingress-integrator) charm
  once the relation has been implemented.
- Outline steps to inject the necessary environment variables (`GDPR_AUDIENCE`
  and `GDPR_SA_EMAIL`) into the charm. This is currently done by modifying the
  original charm code with additional config parameters and re-building the
  charm.
