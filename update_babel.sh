#!/bin/sh

WD=$(dirname $0)

echo "-> enable virtual environment"
. $WD/venv/bin/activate

WD="$WD/moneywatch"

(cd $WD; pybabel extract -F babel.cfg -o messages.pot .)
(cd $WD; pybabel update -i messages.pot -d translations)

