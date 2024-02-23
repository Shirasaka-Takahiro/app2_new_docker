FROM mysql:8.0
COPY ./sql /docker-entrypoint-initdb.d
COPY ./my.cnf /etc/my.cnf
EXPOSE 3306