FROM postgres:alpine

ADD ./docker/create_db.sql /docker-entrypoint-initdb.d/