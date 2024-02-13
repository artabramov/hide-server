FROM ubuntu:22.04
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

ADD . /hide
WORKDIR /hide

RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y python3-pip

RUN pip3 install fastapi[all]==0.109.1
RUN pip3 install uvicorn[standard]==0.27.0.post1
RUN pip3 install SQLAlchemy==2.0.25
RUN pip3 install asyncpg==0.29.0
RUN pip3 install redis==5.0.1
RUN pip3 install pyotp==2.9.0
RUN pip3 install qrcode[pil]==7.4.2
RUN pip3 install aiofiles==23.2.1
RUN pip3 install filetype==1.2.0
RUN pip3 install python-dotenv==1.0.1
RUN pip3 freeze > /hide/requirements.txt

RUN apt-get install -y sudo
RUN apt install -y git
# RUN apt-get install -y cron
# RUN apt-get upgrade -y cron
# RUN apt-get install -y ntp
RUN apt-get install -y redis
RUN apt install -y postgresql

RUN mkdir /var/log/hide
RUN chmod -R 777 /var/log/hide

EXPOSE 80
ENTRYPOINT ["/hide/entrypoint.sh"]
