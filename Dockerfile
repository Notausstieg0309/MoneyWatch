FROM python:3
WORKDIR /usr/src/app

RUN useradd -r moneywatch ; mkdir /data/ ; pip install --upgrade pip ; pip install gunicorn

COPY --chown=moneywatch:moneywatch  . .

RUN pip install --no-cache-dir -e .

USER moneywatch
VOLUME /data
WORKDIR /data

CMD [ "/usr/src/app/docker-entry.sh" ]
