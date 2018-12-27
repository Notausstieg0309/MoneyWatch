#!/bin/sh

if [ ! -d "venv" ]; then
    echo "-> creating python virtual environment"
	python3 -m venv venv
	echo "-> enable virtual environment"
	. venv/bin/activate
	echo "-> installing moneywatch in virtual environment"
	pip3 install -e .
else
    echo "-> enable virtual environment"
	. venv/bin/activate
fi




export FLASK_APP=moneywatch
export FLASK_ENV=development

if [ ! -e "instance/db.sqlite" ]; then
    echo "-> initializing SQLite database"
	flask init-db 
fi

echo "-> starting flask webserver on port 1234"
flask run --host 0.0.0.0 --port 1234
