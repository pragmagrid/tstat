source ../.env
docker run --rm influxdb:${INFLUXDB_VERSION} influxd config > influxdb.conf
