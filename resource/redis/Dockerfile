FROM redis:latest

WORKDIR /scripts
COPY scripts/*.* .
RUN chmod +x *.sh

CMD [ "sh", "/scripts/init-redis.sh" ]
