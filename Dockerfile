FROM centos

# SYSTEMD WORKAROUND
ENV container=docker
COPY container.target /etc/systemd/system/container.target
RUN ln -sf /etc/systemd/system/container.target /etc/systemd/system/default.target
STOPSIGNAL SIGRTMIN+3

# Set the working directory to /root/app
WORKDIR /root/app

# Copy the current directory contents into the container at /root/app
COPY . /root/app

RUN yum -y install epel-release && yum clean all
RUN yum -y install python-pip git rpm-build nginx python-devel mc&& yum clean all
RUN yum -y groupinstall "Development Tools" && yum clean all
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN git config --global user.email "ilya.aurov@gmail.com"
RUN git config --global user.name "Ilya"
RUN sh buildrpm.sh ip2w.spec
RUN rpm -i /root/rpm/RPMS/noarch/ip2w-0.0.1-1.noarch.rpm
RUN useradd -G "nginx" -U otus
RUN chgrp otus /var/log/otus
RUN chmod 774 /var/log/otus
RUN systemctl enable ip2w.service
# Make port 80 available to the world outside this container
EXPOSE 80

COPY ./start_service.sh /

ENTRYPOINT ["/sbin/init"]
