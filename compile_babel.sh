#!/bin/sh

cd $(dirname $0)/moneywatch
pybabel compile -d translations
