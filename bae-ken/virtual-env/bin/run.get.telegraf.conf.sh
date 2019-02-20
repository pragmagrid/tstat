source ../.env
docker run --rm telegraf:${TELEGRAF_VERSION} telegraf config > telegraf.conf
