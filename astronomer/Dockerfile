FROM quay.io/astronomer/ap-airflow:2.1.0-buster

USER root

#RUN apt-get update \
# && apt-get install -y --no-install-recommends chromium-driver libxml2

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

#ADD "https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip" .
#COPY files/* ./
#RUN mkdir -p /data
#CMD [ "python3", "bezrealitky_scrape.py"]
#CMD [ "/bin/bash" ]