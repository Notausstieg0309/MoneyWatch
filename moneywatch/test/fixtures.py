import pytest

from moneywatch import create_app

@pytest.fixture
def app():

    config = {
        TESTING = True,
        SESSION_TYPE="filesystem",
        SQLALCHEMY_DATABASE_URI="sqlite://"
    }

    return create_app(config)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    from moneywatch import db
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db.session.commit()