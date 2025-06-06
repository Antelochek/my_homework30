from .factories import ClientFactory, ParkingFactory
from myhw.main.models import Client, Parking, db

# тест 1
def test_create_client(app, db, client):
    client = ClientFactory()
    db.session.commit()
    assert client.id is not None
    assert len(db.session.query(Client).all()) == 2

#тест 2
def test_create_product(client, db):
    parking = ParkingFactory()
    db.session.commit()
    assert parking.id is not None
    assert len(db.session.query(Parking).all()) == 2
