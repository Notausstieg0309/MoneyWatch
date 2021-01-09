#!/bin/sh

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

echo "-> updating database"
flask db upgrade

echo "-> starting flask webserver on port 1234"
flask run --host 0.0.0.0 --port 1234
