#!/bin/sh

WD=$(dirname $0)

echo "-> enable virtual environment"
. $WD/venv/bin/activate

WD="$WD/moneywatch"

(cd $WD; pybabel compile -d translations)
