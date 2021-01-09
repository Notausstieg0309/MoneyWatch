#!/bin/sh
#
# Execute arbitary flask commands directly within development environment

WD=$(dirname $0)

if [ ! -d "$WD/venv" ]; then
    echo "-> creating python virtual environment"
	python3 -m venv $WD/venv
fi

echo "-> enable virtual environment"
. $WD/venv/bin/activate

export FLASK_APP=moneywatch
export FLASK_ENV=development

echo "-> executing: flask $@ "
flask "$@"
