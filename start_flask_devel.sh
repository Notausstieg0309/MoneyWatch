#!/bin/sh

if [ ! -d "venv" ]; then
    echo "-> creating python virtual environment"
	python3 -m venv venv
fi

echo "-> enable virtual environment"
. venv/bin/activate

echo "-> installing moneywatch in virtual environment"
pip3 install -e .

export FLASK_APP=moneywatch
export FLASK_ENV=development

echo "-> updating database"
flask db upgrade 

echo "-> starting flask webserver on port 1234"
flask run --host 0.0.0.0 --port 1234
