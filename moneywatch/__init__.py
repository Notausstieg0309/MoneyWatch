import os
import logging

from flask import Flask, session, request
from flask_session import Session
from flask_babel import Babel
from babel import negotiate_locale



def create_app(test_config=None):
    
    from moneywatch import ruleset, categories, transactions, overview, utils, importer, ajax
    from moneywatch.utils import db

    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
            SESSION_TYPE="filesystem",
            DATABASE=os.path.join(app.instance_path,'db.sqlite'),
            BABEL_DEFAULT_LOCALE='en',     
            LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            LOGGING_LOCATION = os.path.join(app.instance_path,'moneywatch.log'),
            LOGGING_LEVEL = logging.DEBUG          
    )
    
    
    Session(app)
    babel = Babel(app)
 
    @babel.localeselector
    def get_current_locale():
        preferred = [x.replace('-', '_') for x in request.accept_languages.values()]
        return negotiate_locale(preferred, [str(translation) for translation in babel.list_translations()])
    
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
	
    return app

  
