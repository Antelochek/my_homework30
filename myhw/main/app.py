from datetime import datetime
from typing import List, Any

import pytest
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///park.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
    db.init_app(app)

    from .models import Client, ClientParking, Parking

    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/clients", methods=["POST"])
    def add_client():
        if request.method == "POST":
            name = request.form.get("name", type=str)
            surname = request.form.get("surname", type=str)
            credit_card = request.form.get("credit_card", type=str)
            car_number = request.form.get("car_number", type=str)
            new_client = Client(
                name=name,
                surname=surname,
                credit_card=credit_card,
                car_number=car_number,
            )
            db.session.add(new_client)
            db.session.commit()
            return "", 201

    @app.route("/client_parking", methods=["POST"])
    def client_parking():
        if request.method == "POST":
            client_id = request.form.get("client_id", type=int)
            parking_id = request.form.get("parking_id", type=int)
            client = db.session.query(Client).get(client_id)
            if not client:
                print(f"Клиент с номером {client_id} не найден")
                return None

            parking = (
                db.session.query(Parking)
                .filter(Parking.id == parking_id, Parking.opened == True)
                .first()
            )

            if not parking:
                print("Нет доступных парковочных мест")
                return None

            new_record = ClientParking(
                client_id=client.id,
                parking_id=parking.id,
                time_in=datetime.now(),
                time_out=None,
            )
            parking.count_available_places -= 1

            db.session.add(new_record)
            db.session.commit()

            return f"Место на парковке {parking.address} успешно забронировано", 200

    @app.route("/parking", methods=["POST"])
    def add_parking():
        if request.method == "POST":
            address = request.form.get("address", type=str)
            opened = request.form.get("opened", type=bool)
            count_places = request.form.get("count_places", type=int)
            new_parking = Parking(
                address=address,
                opened=opened,
                count_places=count_places,
                count_available_places=count_places,
            )
            db.session.add(new_parking)
            db.session.commit()
            return jsonify(new_parking.to_json()), 201

    @app.route("/parking", methods=["DELETE"])
    def parking_delete():
        client_id = request.form.get("client_id", type=int)
        parking_id = request.form.get("parking_id", type=int)
        client = db.session.query(Client).get(client_id)
        if not client:
            raise ValueError(f"Клиент с номером {client_id} не найден")
        parking = db.session.query(Parking).get(parking_id)
        if not parking:
            raise ValueError(f"Парковка с ID {parking_id} не найдена")

        parking_record = (
            db.session.query(ClientParking)
            .filter(
                ClientParking.client_id == client_id,
                ClientParking.parking_id == parking_id,
                ClientParking.time_out == None,
            )
            .first()
        )

        if not parking_record:
            raise ValueError(
                f"Активная парковка для клиента {client_id} на парковке ID {parking_id} не найдена"
            )

        parking_record.time_out = datetime.now()

        parking.count_available_places += 1

        if parking.count_available_places > parking.count_places:
            parking.count_available_places = parking.count_places

        db.session.commit()
        return f"клиент {client_id} успешно выехал с парковки {parking.address}", 200

    @app.route("/clients", methods=["GET"])
    def get_clients():
        """Получение пользователей"""
        users: List[Client] = db.session.query(Client).all()
        users_list = [u.to_json() for u in users]
        return jsonify(users_list), 200

    @app.route("/clients/<int:user_id>", methods=["GET"])
    def get_client_id(user_id: int):
        """Получение пользователя по ид"""
        user: Any  = db.session.query(Client).get(int(user_id))
        return jsonify(user.to_json()), 200

    @app.route("/parking", methods=["GET"])
    def get_parking():
        parking_d = db.session.query(Parking).all()

        if not parking_d:
            return jsonify({"error": "Parking not found"}), 404
        parking_list = [p.to_json() for p in parking_d]

        return jsonify(parking_list), 200

    @app.route("/parking/<int:parking_id>", methods=["GET"])
    def get_parking_id(parking_id):
        parking_d = Parking.query.get(parking_id)

        if not parking_d:
            return jsonify({"error": "Parking not found"}), 404
        return jsonify(parking_d.to_json()), 201

    return app


GET_ENDPOINTS : List[tuple] = [
    ("/clients", {}),  # Список клиентов
    ("/clients/1", {}),  # Конкретный клиент
    ("/parking", {}),  # Список парковок
    ("/parking/1", {}),  # Конкретная парковка
]
