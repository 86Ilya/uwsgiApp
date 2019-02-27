FROM centos

# Set the working directory to /root/app
WORKDIR /root/app

# Copy the current directory contents into the container at /root/app
COPY . /root/app

# Install any needed packages specified in requirements.txt
RUN yum -y install epel-release && yum clean all
RUN yum -y install python-pip git rpm-build nginx python-devel supervisor && yum clean all
RUN yum -y groupinstall "Development Tools" && yum clean all
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN git config --global user.email "ilya.aurov@gmail.com"
RUN git config --global user.name "Ilya"
RUN cat supervisord.conf >> /etc/supervisord.conf
RUN sh buildrpm.sh ip2w.spec
RUN rpm -i /root/rpm/RPMS/noarch/ip2w-0.0.1-1.noarch.rpm
# Make port 80 available to the world outside this container
EXPOSE 80


# CMD ['/usr/bin/supervisord', 'nc', '/etc/supervisord.conf']
CMD /usr/bin/supervisord -nc /etc/supervisord.conf
