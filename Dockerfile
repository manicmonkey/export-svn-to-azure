FROM ubuntu:15.04

RUN apt-get update && \
    apt-get install -y python wget && \
    apt-get install -y python-dev libffi-dev libssl-dev build-essential python-pip subversion

RUN pip install azure svn

ADD azure_upload.py /opt/
RUN chmod +x /opt/azure_upload.py

ENTRYPOINT ["/opt/azure_upload.py"]