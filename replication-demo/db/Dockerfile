FROM postgres
RUN apt-get -y update && \
    apt-get -y install iputils-ping dnsutils
COPY docker-entrypoint.sh /usr/local/bin