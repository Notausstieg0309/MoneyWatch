#!/bin/sh
export FLASK_APP="moneywatch:create_app(instance_path='/data')"

flask db upgrade
gunicorn --workers 4 --bind 0.0.0.0 -m 007 'moneywatch:create_app(instance_path="/data")'