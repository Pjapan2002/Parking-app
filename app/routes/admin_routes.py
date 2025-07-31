from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from collections import defaultdict
from datetime import datetime
from ..models import ParkingLot, ParkingSpot, User, Reservation

from ..models import User
from ..db import db

admin = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(func):
    # Simple decorator to restrict route to admins
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access only.", "danger")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper


@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))

    users = User.query.filter_by(is_admin=False).all()
    lots = ParkingLot.query.all()
    reservations = Reservation.query.all()

    # Bookings per day
    bookings_by_date = defaultdict(int)
    for res in reservations:
        date_str = res.parking_time.strftime('%Y-%m-%d')
        bookings_by_date[date_str] += 1

    booking_labels = list(bookings_by_date.keys())
    booking_data = list(bookings_by_date.values())

    # Occupancy per lot
    occupancy_labels = []
    available_counts = []
    occupied_counts = []

    for lot in lots:
        spots = lot.spots
        occupancy_labels.append(lot.prime_location_name)
        available = sum(1 for spot in spots if spot.status == "A")
        occupied = sum(1 for spot in spots if spot.status == "O")
        lot.available_spots = sum(1 for spot in spots if spot.status == "A")
        available_counts.append(available)
        occupied_counts.append(occupied)

    # Active users with full reservation info
    active_reservations = (
        db.session.query(Reservation)
        .join(User)
        .join(ParkingSpot)
        .join(ParkingLot)
        .filter(Reservation.leaving_time == None)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        lots=lots,
        reservations=reservations,
        active_reservations=active_reservations,
        users=users,
        booking_labels=booking_labels,
        booking_data=booking_data,
        occupancy_labels=occupancy_labels,
        available_counts=available_counts,
        occupied_counts=occupied_counts
    )


@admin.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Optional: prevent deletion of admin
    if user.is_admin:
        flash("Admin account cannot be deleted.", "danger")
        return redirect(url_for("admin.dashboard"))

    # Delete user's reservations too
    Reservation.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route('/user/history/<int:user_id>')
@login_required
def user_history(user_id):
    user = User.query.get_or_404(user_id)
    reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parking_time.desc()).all()
    return render_template("admin/user_history.html", user=user, reservations=reservations)



@admin.route("/add_lot", methods=["GET", "POST"])
@login_required
@admin_required
def add_lot():
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        pin = request.form["pin"]
        price = float(request.form["price"])
        max_spots = int(request.form["max_spots"])

        lot = ParkingLot(
            prime_location_name=name,
            address=address,
            pin_code=pin,
            price_per_hour=price,
            maximum_number_of_spots=max_spots
        )
        db.session.add(lot)
        db.session.commit()

        # Auto create parking spots
        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)

        db.session.commit()
        flash("Parking lot added successfully with spots!", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/add_lot.html")


@admin.route("/delete_lot/<int:lot_id>")
@login_required
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = any(spot.status == 'O' for spot in lot.spots)
    if occupied:
        flash("Can't delete lot with occupied spots.", "danger")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted.", "info")
    return redirect(url_for("admin.dashboard"))


@admin.route('/lot/edit/<int:lot_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lot(lot_id):
    if not current_user.is_admin:
        abort(403)

    lot = ParkingLot.query.get_or_404(lot_id)

    occupied_spots = sum(1 for spot in lot.spots if spot.status == "O")

    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_hour = float(request.form['price_per_hour'])
        lot.maximum_number_of_spots = int(request.form['max_spots'])
        db.session.commit()

        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_lot.html', lot=lot, occupied_spots=occupied_spots)


@admin.route("/reservations")
@login_required
@admin_required
def view_reservations():
    reservations = Reservation.query.all()
    return render_template("admin/reservations.html", reservations=reservations)


@admin.route('/force-release/<int:reservation_id>', methods=['POST'])
@login_required
@admin_required
def force_release(reservation_id):
    if not current_user.is_admin:
        abort(403)

    reservation = Reservation.query.get_or_404(reservation_id)

    # Mark as released
    reservation.leaving_time = datetime.utcnow()
    reservation.spot.status = "A"
    db.session.commit()

    flash(f"Spot {reservation.spot.id} has been force-released.", "warning")
    return redirect(url_for('admin.dashboard'))
