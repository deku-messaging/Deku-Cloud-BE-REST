#!/usr/bin/bash
docker build --target production -t deku-cloud . && \
docker run \
-v ${SSL_FILE_PATH:?err}:${SSL_FILE_PATH} \
-p ${PORT}:${PORT} -p ${SSL_PORT}:${SSL_PORT} \
-d --name deku-cloud --env-file .env deku-cloud