---
---

# ISS - Kamaji Web Service

> [!IMPORTANT]
> This documentation page is still **under construction**.

**Brief**: The Kamaji Web Service consists of the entire pipeline designed to get jobs to avionics testing boards. It includes services such as the **API**, the **webserver**, **load balancer**, **database**, and **proxy** to give a cohesive experience.

The entire system is dockerized in a single `docker-compose` image, which spins up the other docker containers needed for the service. To orchestrate the startup process, first **build** the container:

```
$ docker-compose -f ./compose.yml build
```

Then it can be run with

```
$ docker-compose -f ./compose.yml up
```

The same sequence of commands works for the production environment, except with a different **.yml** file:

```
$ docker-compose -f ./compose.prod.yml build
$ docker-compose -f ./compose.prod.yml up
```
## API
The API is currently in development, as such, its documentation is held in a living document over at [the Kamaji Google Doc](https://docs.google.com/document/d/1iDN4tgLmHv-DWganUn9Wvn14B_rqZOBI2Ggfk1amGuE/edit#heading=h.s803wgkbrl4z).

## Webserver
The webserver, which hosts the React page which interfaces with our users is run as part of the container in the brief section of this page. However, the react app can be run as a standalone app by executing the following commands:

```
$ npm install
$ npm run coldstart
```

in the `hilsim-web` directory.

## Database
The database uses `postgres 16.1`, available from the `postgres` image on [Dockerhub](https://hub.docker.com/_/postgres). The schema of the database is described in the API documentation [here](https://docs.google.com/document/d/1iDN4tgLmHv-DWganUn9Wvn14B_rqZOBI2Ggfk1amGuE/edit#heading=h.s803wgkbrl4z).

An **Adminer** view (`4.8.1`,  [Dockerhub](https://hub.docker.com/_/adminer)) is available for administrators to access the database through the `/dbadmin` page. The password for this database is set through a docker secret, and is unique to every installation of the Kamaji service.

## Load balancer
The load balancer constitutes one of the subservices of the **API**, and is mainly handled through the manager thread/board thread architecture described in the preface to `API/internal/threads.py`

In brief: A manager thread spins up a new datastreaming thread for every connection it recieves from a Datastreamer board, and uses that datastreaming thread to communicate to the avionics stack.

## Proxy
The Kamaji proxy combines all these services into one umbrella by directing traffic depending on where it comes in from on port `80`.

`/` is directed to the **webserver**
`/api/` is directed to the **API**
`/dbadmin/` is directed to **Adminer**
`/api/dscomm/ws` specifically is directed to the **Datastreamer Websocket Server** established on port `5001`.

