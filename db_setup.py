from app import create_app
from app.db import db
from app.models.models import User, ParkingLot, ParkingSpot
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()

    print("Creating tables...")
    db.create_all()

    print("Creating admin user...")
    admin = User(
        username="admin",
        password=generate_password_hash("admin123"),
        is_admin=True
    )
    db.session.add(admin)

    print("Creating sample users...")
    user1 = User(username="japan", password=generate_password_hash("japan123"), is_admin=False)
    user2 = User(username="krisha", password=generate_password_hash("krisha123"), is_admin=False)
    db.session.add_all([user1, user2])

    print("Creating sample parking lots...")
    lot1 = ParkingLot(
        prime_location_name="Smart Valet Parking",
        address="Smart Valet Parking, Vesu, Surat",
        pin_code="395007",
        price_per_hour=30.0,
        maximum_number_of_spots=5
    )
    lot2 = ParkingLot(
        prime_location_name="Vitoria Hills",
        address="Vitoria Hills, Adajan, Surat",
        pin_code="395009",
        price_per_hour=25.0,
        maximum_number_of_spots=3
    )
    db.session.add_all([lot1, lot2])
    db.session.commit()

    print("Creating parking spots for each lot...")
    def create_spots(lot):
        for _ in range(lot.maximum_number_of_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)

    create_spots(lot1)
    create_spots(lot2)

    db.session.commit()
    print("Admin username: 'admin', password: 'admin123'")
