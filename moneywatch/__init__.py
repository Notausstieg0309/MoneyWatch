import os
import logging

from flask import Flask, session, request
from flask_session import Session
from flask_babel import Babel
from flask_migrate import Migrate
from babel import negotiate_locale



def create_app(test_config=None):
    
    from moneywatch import ruleset, categories, transactions, overview, utils, importer, ajax, accounts, analysis
    from moneywatch.utils.objects import db,Account

    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_mapping(
            SESSION_TYPE="filesystem",
            SQLALCHEMY_DATABASE_URI="sqlite:///"+os.path.join(app.instance_path,'db.sqlite'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            #SQLALCHEMY_ECHO=True,
            #SQLALCHEMY_RECORD_QUERIES=True, 
            BABEL_DEFAULT_LOCALE='en',     
            LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            LOGGING_LOCATION = os.path.join(app.instance_path,'moneywatch.log'),
            LOGGING_LEVEL = logging.DEBUG          
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
        
    @babel.localeselector
    def get_current_locale():
        preferred = [x.replace('-', '_') for x in request.accept_languages.values()]
        return negotiate_locale(preferred, [str(translation) for translation in babel.list_translations()])
    
    
    @app.context_processor
    def context_processor():
        return dict(accounts_list=Account.query.with_entities(Account.id, Account.name).order_by(Account.id.asc()).all())
    
    
   
    
    
    # Configure logging
    handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
    handler.setLevel(app.config['LOGGING_LEVEL'])
    
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
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
    
    return app

  
