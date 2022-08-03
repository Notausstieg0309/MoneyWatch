import pytest
import datetime

from moneywatch import create_app


@pytest.fixture
def app():

    config = {
        "TESTING": True,
        "SESSION_TYPE": "filesystem",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    }

    return create_app(config)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    from moneywatch.utils.objects import db
    with app.app_context():
        db.create_all()
        yield db
        db.session.rollback()
        db.drop_all()



@pytest.fixture
def fixed_date(monkeypatch):

    original_date = datetime.date

    def with_metaclass(meta, *base_cls):
        return meta("NewBaseCls", base_cls, {})

    class fixeddate_meta(type):
        def __instancecheck__(self, instance):
            return isinstance(instance, original_date)

    class fixeddate(with_metaclass(fixeddate_meta, original_date)):
        _today_date = datetime.date.today()

        @classmethod
        def today(self):
            return self._today_date

        @classmethod
        def set_today(self, *args, **kwargs):
            self._today_date = datetime.date(*args, **kwargs)

        @classmethod
        def set_today_date(self, new_date):
            if isinstance(new_date, datetime.date):
                self._today_date = new_date

    fixeddate.__name__ = "datetime.date"
    monkeypatch.setattr(datetime, 'date', fixeddate)
