import os
import logging
import click

from flask import Flask, request, send_file, abort
from flask_session import Session
from flask_babel import Babel
from flask_migrate import Migrate
from flask_assets import Environment, Bundle
from babel import negotiate_locale



def create_app(test_config=None):

    from moneywatch import ruleset, categories, transactions, overview, importer, ajax, accounts, analysis
    from moneywatch.utils.objects import db, Account

    app = Flask(__name__, instance_relative_config=True)

    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_mapping(
            SESSION_TYPE="filesystem",
            SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, 'db.sqlite'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            # SQLALCHEMY_ECHO=True,
            # SQLALCHEMY_RECORD_QUERIES=True,
            BABEL_DEFAULT_LOCALE='en',
            LOGGING_FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            LOGGING_LOCATION=os.path.join(app.instance_path, 'moneywatch.log'),
            LOGGING_LEVEL=logging.DEBUG
        )


    Session(app)
    babel = Babel(app)

    db.init_app(app)

    migrate = Migrate(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations"))

    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)

    assets = Environment(app)

    bundles = {

        # JS
        'base_js': Bundle(
            'jquery.min.js',
            'materialize.min.js',
            'common_materialize.js',
            output='base.%(version)s.assets.js',
            merge=True,
            filters='rjsmin'),

        'analysis_js': Bundle(
            'Chart.bundle.min.js',
            'analysis.js',
            output='analysis.%(version)s.assets.js',
            merge=True,
            filters='rjsmin'),

        'overview_js': Bundle(
            'Chart.bundle.min.js',
            'overview_modals.js',
            output='overview.%(version)s.assets.js',
            merge=True,
            filters='rjsmin'),

        # CSS
        'base_css': Bundle(
            'materialize.min.css',
            'materialize.icons.css',
            'materialize.custom.css',
            output='base.%(version)s.assets.css',
            filters='cssmin'),
    }

    assets.register(bundles)

    @babel.localeselector
    def get_current_locale():
        preferred = [x.replace('-', '_') for x in request.accept_languages.values()]
        return negotiate_locale(preferred, [str(translation) for translation in babel.list_translations()])


    @app.context_processor
    def context_processor():
        return dict(accounts_list=Account.query.with_entities(Account.id, Account.name).order_by(Account.id.asc()).all())

    # create a demo database // ATTENTION: THIS COMMAND WIPES YOUR LOCAL DATABASE
    @app.cli.command("create-demo")
    @click.argument("plugin", required=True, type=str)
    @click.option("--offset", type=click.IntRange(min=0))
    def create_demo(plugin, offset):
        print("using plugin: %s" % plugin)
        from moneywatch.utils.demo import create_demo_db
        from moneywatch.importer import plugins

        if not plugins.plugin_loaded(plugin):
            print("unavailable plugin: %s" % plugin)
            return

        # create the demo database and retrieve all importable items
        importer_items = create_demo_db(offset)

        print("creating import file via plugin '%s'" % plugin)

        filename = None

        with open(os.path.join(app.instance_path, "demo_import_content"), "wb") as f:
            # create the import file by using the selected plugin
            filename = plugins.create_file(importer_items, f, plugin)

        with open(os.path.join(app.instance_path, "demo_import_filename"), "w") as f:
            f.write(filename)

        print("successfuly created demo databaase. You can download the import file by accessing '/demo' via web browser")

    # Configure logging
    handler = logging.FileHandler(app.config.get('LOGGING_LOCATION', os.path.join(app.instance_path, 'moneywatch.log')))
    handler.setLevel(app.config.get('LOGGING_LEVEL', logging.INFO))

    formatter = logging.Formatter(app.config.get('LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register database commands
    db.init_app(app)

    app.register_blueprint(ruleset.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(overview.bp)
    app.register_blueprint(importer.bp)
    app.register_blueprint(ajax.bp)
    app.register_blueprint(accounts.bp)
    app.register_blueprint(analysis.bp)


    @app.route("/demo")
    def demo_download():

        if os.path.exists(os.path.join(app.instance_path, "demo_import_content")) and os.path.exists(os.path.join(app.instance_path, "demo_import_filename")):
            with open(os.path.join(app.instance_path, "demo_import_filename")) as f:
                filename = f.readline()
            return send_file(os.path.join(app.instance_path, "demo_import_content"), as_attachment=True, attachment_filename=filename.strip(), cache_timeout=-1)
        else:
            return abort(404)

    return app

