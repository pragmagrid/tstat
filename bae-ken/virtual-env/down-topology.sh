docker-compose -f ./influxdb/docker-compose.yml down -d && \
docker-compose -f ./grafana/docker-compose.yml down -d && \
docker-compose -f ./grafana-2/docker-compose.yml down -d && \
docker-compose -f ./telegraf/docker-compose.yml down -d && \
docker-compose -f ./kapacitor/docker-compose.yml down -d && \
docker-compose -f ./kapacitor-2/docker-compose.yml down -d && \
docker-compose -f ./chronograf/docker-compose.yml down -d && \
docker-compose -f ./chronograf-2/docker-compose.yml down -d 

