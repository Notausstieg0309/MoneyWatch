FROM python:3
WORKDIR /usr/src/app

RUN mkdir /data/ ; pip install --upgrade pip ; pip install gunicorn

COPY . .

RUN pip install --no-cache-dir -e . ; chmod +x docker-entry.sh

VOLUME /data
WORKDIR /data

CMD [ "/usr/src/app/docker-entry.sh" ]