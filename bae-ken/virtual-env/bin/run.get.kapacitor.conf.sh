source ../.env
docker run --rm kapacitor:${KAPACITOR_VERSION} kapacitord config > kapacitor.conf
