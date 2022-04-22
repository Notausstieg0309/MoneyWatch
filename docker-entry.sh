#!/bin/sh
flask db upgrade
gunicorn --workers 4 -m 007 'moneywatch:create_app()'