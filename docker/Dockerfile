FROM python:3.8-buster
WORKDIR /app
COPY files/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
#ADD "https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip" .
RUN apt-get update && apt-get install -y chromium-driver
COPY files/* ./
RUN mkdir -p /data
#CMD [ "python3", "bezrealitky_scrape.py"]
CMD [ "/bin/bash" ]
