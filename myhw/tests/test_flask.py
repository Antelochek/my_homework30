import json
from datetime import datetime

from myhw.main.app import db as _db
from myhw.main.models import ClientParking, Parking


def test_get_all_clients(client):
    """Тест получения списка всех клиентов"""
    response = client.get("/clients")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Test"


def test_get_client_by_id(client):
    """Тест получения клиента по ID"""
    response = client.get("/clients/1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Test"
    assert data["surname"] == "User"


def test_create_client(client):
    """Тест создания нового клиента"""
    new_client = {
        "name": "New",
        "surname": "Client",
        "car_number": "B456CD",
        "credit_card": "8765432187654321",
    }
    response = client.post("/clients", data=new_client)
    assert response.status_code == 201

    response = client.get("/clients")
    data = json.loads(response.data)
    assert len(data) == 2


def test_create_parking(client):
    """Тест создания новой парковочной зоны"""
    new_parking = {"address": "New Parking", "opened": True,
                   "count_places": 20}
    response = client.post("/parking", data=new_parking)
    assert response.status_code == 201

    # Проверяем, что парковка действительно создана
    response = client.get("/parking")
    data = json.loads(response.data)
    assert len(data) == 2


def test_park_car(client):
    """Тест заезда на парковку"""
    parking_data = {"client_id": 1, "parking_id": 1}
    response = client.post("/client_parking", data=parking_data)
    assert response.status_code == 200

    # Проверяем, что место занято
    response = client.get("/parking/1")
    data = json.loads(response.data)
    assert data["count_available_places"] == 9

    # Проверяем, что запись о парковке создана
    parking_record = ClientParking.query.first()
    assert parking_record is not None
    assert parking_record.time_out is None


def test_unpark_car(client):
    """Тест выезда с парковки"""
    # Сначала создаем запись о парковке
    test_parking = ClientParking(client_id=1, parking_id=1,
                                 time_in=datetime.now())
    _db.session.add(test_parking)
    _db.session.commit()

    # Уменьшаем количество свободных мест
    parking = Parking.query.get(1)
    parking.count_available_places = 9
    _db.session.commit()

    # Теперь тестируем выезд
    parking_data = {"client_id": 1, "parking_id": 1}
    response = client.delete("/parking", data=parking_data)
    assert response.status_code == 200

    # Проверяем, что место освободилось
    response = client.get("/parking/1")
    data = json.loads(response.data)
    assert data["count_available_places"] == 10

    # Проверяем, что время выезда установлено
    parking_record = ClientParking.query.first()
    assert parking_record.time_out is not None
