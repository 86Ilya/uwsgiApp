FROM centos

# SYSTEMD WORKAROUND
ENV container=docker
COPY ./docker_deploy/container.target /etc/systemd/system/container.target
RUN ln -sf /etc/systemd/system/container.target /etc/systemd/system/default.target
STOPSIGNAL SIGRTMIN+3

# Set the working directory to /root/app
WORKDIR /root/app

COPY ./ip2w-0.0.1-1.noarch.rpm /root/app/
COPY ./requirements.txt /root/app/
COPY ./tests /root/app/tests

RUN yum -y install epel-release && yum clean all
RUN yum -y install python-pip git rpm-build nginx python-devel && yum clean all
RUN yum -y groupinstall "Development Tools" && yum clean all
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN rpm -i /root/app/ip2w-0.0.1-1.noarch.rpm
RUN useradd -G "nginx" -U otus
RUN chgrp otus /var/log/otus
RUN chmod 774 /var/log/otus
RUN systemctl enable ip2w.service
# Make port 80 available to the world outside this container
EXPOSE 80

COPY ./docker_deploy/start_service.sh /

ENTRYPOINT ["/sbin/init"]
