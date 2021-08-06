FROM ubuntu:20.04

USER root
RUN apt-get update && apt-get install -y tzdata
RUN apt-get install -y wget cmake clang git
RUN apt-get -y install sudo

RUN sudo ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN sudo dpkg-reconfigure -f noninteractive tzdata
RUN mkdir /developer

WORKDIR /developer

RUN apt-get update && apt-get clean
RUN apt-get -y install libxml2-dev libxslt-dev liblept5 python-dev python3-pip locales clang

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pip3 install --upgrade pip

COPY . .

RUN pip3 install --ignore-installed -r requirements.txt

RUN python3 download_punkt.py

ENV FLASK_APP app.py

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:5050"]
