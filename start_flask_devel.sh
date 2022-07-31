#!/bin/bash

WD=$(dirname $0)

if [ ! -d "$WD/venv" ]; then
    echo "-> creating python virtual environment"
	python3 -m venv $WD/venv
fi

echo "-> enable virtual environment"
. $WD/venv/bin/activate

echo "-> installing moneywatch in virtual environment"
pip3 install -e $WD/.

export FLASK_APP=moneywatch
export FLASK_ENV=development
export FLASK_RUN_EXTRA_FILES="$(ls -1 src/moneywatch/translations/*/LC_MESSAGES/messages.mo)"

echo "-> updating database"
flask db upgrade

echo "-> starting flask webserver on port 1234"
flask run --host 0.0.0.0 --port 1234
