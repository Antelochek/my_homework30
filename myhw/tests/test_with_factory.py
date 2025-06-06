from myhw.main.models import Client, Parking

from .factories import ClientFactory, ParkingFactory


# тест 1
def test_create_client(app, client, db):
    client = ClientFactory()
    db.session.commit()
    assert client.id is not None
    assert len(db.session.query(Client).all()) == 2


def test_create_product(client, db):
    parking = ParkingFactory()
    db.session.commit()
    assert parking.id is not None
    assert len(db.session.query(Parking).all()) == 2
