FROM python:3
LABEL author="Edo Reggiani"
LABEL version="0.1" 

# set work directory
WORKDIR /usr/src/strava_api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat

COPY requirements.txt /usr/src/strava_api/
RUN pip install --no-cache-dir -r /usr/src/strava_api/requirements.txt
COPY . /usr/src/strava_api/

