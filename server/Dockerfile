# syntax=docker/dockerfile:1
FROM alpine:3.10.6

RUN apk update
RUN apk add --no-cache pngcrush
RUN apk add --no-cache inkscape
RUN apk add --no-cache python3 py3-pip
RUN apk add --no-cache ttf-dejavu
RUN apk add --no-cache tzdata

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /bin/kindledashboard/

COPY kindledashboard_preprocess.svg kindledashboard_preprocess.svg
COPY app.py app.py
COPY ./googlecalendar/ googlecalendar/
COPY ./mail/ mail/
COPY ./notes/ notes/

COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

EXPOSE 5123:5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]