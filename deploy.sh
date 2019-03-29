#!/usr/bin/env bash


docker build --tag ip2w_service:systemd -f docker_deploy/Dockerfile .
docker run \
  --detach \
  --name=ip2w-systemd \
  --mount type=bind,source=/sys/fs/cgroup,target=/sys/fs/cgroup \
  --mount type=bind,source=/sys/fs/fuse,target=/sys/fs/fuse \
  --mount type=tmpfs,destination=/run \
  --mount type=tmpfs,destination=/run/lock ip2w_service:systemd \

docker exec -it ip2w-systemd "/start_service.sh"
ipaddr=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ip2w-systemd`
echo "Service endpoint is: http://$ipaddr/ip2w/"
