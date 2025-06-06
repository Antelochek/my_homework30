import factory
from faker import Faker

from myhw.main.models import Client, Parking, db

fake = Faker()


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.LazyAttribute(
        lambda x: fake.credit_card_number() if fake.boolean() else None
    )
    car_number = factory.LazyFunction(lambda: fake.license_plate())


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    opened = factory.Faker("boolean")
    count_places = factory.Faker("random_int", min=10, max=100)
    count_available_places = factory.LazyAttribute(lambda o: o.count_places)
