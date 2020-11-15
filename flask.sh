#!/bin/sh
#
# Execute arbitary flask commands directly within development environment

if [ ! -d "venv" ]; then
    echo "-> creating python virtual environment"
	python3 -m venv venv
fi

echo "-> enable virtual environment"
. venv/bin/activate

export FLASK_APP=moneywatch
export FLASK_ENV=development

echo "-> executing: flask $@ "
flask "$@"
