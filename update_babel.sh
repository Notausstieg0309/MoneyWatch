#!/bin/sh
cd $(dirname $0)/moneywatch

pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations

