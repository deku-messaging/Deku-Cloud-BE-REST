# Configurations

## Table of contents

1. [Requirements](#requirements)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [How to use](#how-to-use)
5. [Docker](#docker)
6. [Logger](#logger)

## Requirements

- [Python](https://www.python.org/) (version >=
  [3.8.10](https://www.python.org/downloads/release/python-3810/))
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [RabbitMQ](https://www.rabbitmq.com/download.html)
- [MySQL](https://www.mysql.com/) (version >= 8.0.28)
  ([MariaDB](https://mariadb.org/))

## Dependencies

On Ubuntu

```bash
$ sudo apt install python3-dev libmysqlclient-dev apache2 apache2-dev make libapache2-mod-wsgi-py3
```

## Linux Environment Variables

Variables used for the Project:

- MYSQL_DATABASE=STRING
- MYSQL_HOST=STRING
- MYSQL_PASSWORD=STRING
- MYSQL_USER=STRING
- HOST=STRING
- PORT=STRING
- ORIGINS=ARRAY
- SSL_SERVER_NAME=STRING
- SSL_PORT=STRING
- SSL_CERTIFICATE=PATH
- SSL_KEY=PATH
- SSL_PEM=PATH
- RABBITMQ_USER=STRING
- RABBITMQ_PASSWORD=STRING
- RABBITMQ_HOST=STRING
- RABBITMQ_SSL_ACTIVE=STRING
- RABBITMQ_MANAGEMENT_PORT_SSL=STRING
- RABBITMQ_SERVER_PORT_SSL=STRING
- RABBITMQ_SSL_CACERT=PATH
- RABBITMQ_SSL_CRT=PATH
- RABBITMQ_SSL_KEY=PATH

## Installation

### Pip

```bash
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

## How to use

### Start API

**Python**

```bash
$ MYSQL_DATABASE= \
  MYSQL_HOST= \
  MYSQL_PASSWORD= \
  MYSQL_USER= \
  HOST= \
  PORT= \
  ORIGINS= \
  SSL_SERVER_NAME= \
  SSL_PORT= \
  SSL_CERTIFICATE= \
  SSL_KEY= \
  SSL_PEM= \
  RABBITMQ_USER= \
  RABBITMQ_PASSWORD= \
  RABBITMQ_HOST= \
  RABBITMQ_SSL_ACTIVE= \
  RABBITMQ_MANAGEMENT_PORT_SSL= \
  RABBITMQ_SERVER_PORT_SSL= \
  RABBITMQ_SSL_CACERT= \
  RABBITMQ_SSL_CRT= \
  RABBITMQ_SSL_KEY= \
  MODE=production \
  python3 server.py
```

**MOD_WSGI**

```bash
$ MYSQL_DATABASE= \
  MYSQL_HOST= \
  MYSQL_PASSWORD= \
  MYSQL_USER= \
  HOST= \
  PORT= \
  ORIGINS= \
  SSL_SERVER_NAME= \
  SSL_PORT= \
  SSL_CERTIFICATE= \
  SSL_KEY= \
  SSL_PEM= \
  RABBITMQ_USER= \
  RABBITMQ_PASSWORD= \
  RABBITMQ_HOST= \
  RABBITMQ_SSL_ACTIVE= \
  RABBITMQ_MANAGEMENT_PORT_SSL= \
  RABBITMQ_SERVER_PORT_SSL= \
  RABBITMQ_SSL_CACERT= \
  RABBITMQ_SSL_CRT= \
  RABBITMQ_SSL_KEY= \
  MODE=production \
  mod_wsgi-express start-server wsgi_script.py \
  --user www-data \
  --group www-data \
  --port '${PORT}' \
  --ssl-certificate-file '${SSL_CERTIFICATE}' \
  --ssl-certificate-key-file '${SSL_KEY}' \
  --ssl-certificate-chain-file '${SSL_PEM}' \
  --https-only \
  --server-name '${SSL_SERVER_NAME}' \
  --https-port '${SSL_PORT}'
```

## Docker

### Build

Build deku-cloud development docker image

```bash
$ docker build --target development -t deku-cloud .
```

Build deku-cloud production docker image

```bash
$ docker build --target production -t deku-cloud .
```

### Run

Run deku-cloud development docker image. Fill in all the neccessary
[environment variables](#linux-environment-variables)

```bash
$ docker run -d -p 9000:9000 \
  --name deku-cloud \
  --env 'MYSQL_DATABASE=' \
  --env 'MYSQL_HOST=' \
  --env 'MYSQL_PASSWORD=' \
  --env 'MYSQL_USER=' \
  --env 'HOST=' \
  --env 'PORT=' \
  --env 'ORIGINS=' \
  --env 'RABBITMQ_USER=' \
  --env 'RABBITMQ_PASSWORD=' \
  --env 'RABBITMQ_HOST=' \
  deku-cloud
```

Run deku-cloud production docker image. Fill in all the neccessary
[environment variables](#linux-environment-variables)

```bash
$ docker run -d -p 9000:9000 \
  --name deku-cloud \
  --env 'MYSQL_DATABASE=' \
  --env 'MYSQL_HOST=' \
  --env 'MYSQL_PASSWORD=' \
  --env 'MYSQL_USER=' \
  --env 'HOST=' \
  --env 'PORT=' \
  --env 'ORIGINS=' \
  --env 'SSL_SERVER_NAME=' \
  --env 'SSL_PORT=' \
  --env 'SSL_CERTIFICATE=' \
  --env 'SSL_KEY=' \
  --env 'SSL_PEM=' \
  --env 'RABBITMQ_USER=' \
  --env 'RABBITMQ_PASSWORD=' \
  --env 'RABBITMQ_HOST=' \
  --env 'RABBITMQ_SSL_ACTIVE=' \
  --env 'RABBITMQ_MANAGEMENT_PORT_SSL=' \
  --env 'RABBITMQ_SERVER_PORT_SSL=' \
  deku-cloud
```

> Read in a file of environment variables with `--env-file` command e.g.
> `docker run -d -p 9000:9000 --name deku-cloud --env-file myenv.txt deku-cloud`

> Mount path to SSL files with volume `-v` command e.g.
> `docker run -v /host/path/to/certs:/container/path/to/certs -d -p 9000:9000 --name deku-cloud --env-file myenv.txt deku-cloud`

## logger

### Python

```bash
$ python3 server.py --logs=debug
```

### Docker

Container logs

```bash
$ docker logs deku-cloud
```
