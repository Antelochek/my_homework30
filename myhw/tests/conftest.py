import pytest
from myhw.main.app import create_app, db as _db
from myhw.main.models import Client, Parking, ClientParking


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///park.db"
    _app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Устанавливаем контекст приложения
    with _app.app_context():
        _db.create_all()
        yield _app  # Здесь возвращаем само приложение, а не клиент
        _db.drop_all()

    with _app.app_context():
        _db.create_all()
        # Добавляем тестовые данные
        test_client = Client(
            name="Test",
            surname="User",
            car_number="A123BC",
            credit_card="1234567812345678"
        )
        test_parking = Parking(
            address="Test Address",
            opened=True,
            count_places=10,
            count_available_places=10
        )
        _db.session.add(test_client)
        _db.session.add(test_parking)
        _db.session.commit()



@pytest.fixture
def client(app):
    client = app.test_client()
    yield client

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
