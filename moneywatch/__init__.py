import os

from flask import Flask, session, request
from flask_session import Session
from flask_babel import Babel




def create_app(test_config=None):

    from moneywatch import ruleset, categories, transactions, overview, utils, importer

    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
            SECRET_KEY='dev',
            SESSION_TYPE="filesystem",
            DATABASE=os.path.join(app.instance_path,'db.sqlite'),
            BABEL_DEFAULT_LOCALE='en',         
           
    )


    Session(app)
    babel = Babel(app)
    
    @babel.localeselector 
    def get_locale():
        translations = [str(translation) for translation in babel.list_translations()]
        lang = request.accept_languages.best_match(translations)
        return lang   

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass



    app.register_blueprint(ruleset.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(overview.bp)
    app.register_blueprint(importer.bp)
   
        
    
    return app

  
