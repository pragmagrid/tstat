docker-compose -f ./grafana/docker-compose.yml up -d && \
docker-compose -f ./grafana-2/docker-compose.yml up -d && \
docker-compose -f ./telegraf/docker-compose.yml up -d && \
docker-compose -f ./kapacitor/docker-compose.yml up -d && \
docker-compose -f ./kapacitor-2/docker-compose.yml up -d && \
docker-compose -f ./chronograf/docker-compose.yml up -d && \
docker-compose -f ./chronograf-2/docker-compose.yml up -d 

