from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from ..db import db
from ..models import ParkingLot, ParkingSpot, Reservation
from ..forms import UserEditForm

user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    query = ParkingLot.query

    # Check if user submitted search/filter form
    search_text = request.args.get('search')
    available_only = request.args.get('available')

    if search_text:
        query = query.filter(
            ParkingLot.prime_location_name.ilike(f'%{search_text}%') |
            ParkingLot.pin_code.ilike(f'%{search_text}%')
        )

    lots = query.all()

    # If filter for available lots
    if available_only:
        lots = [lot for lot in lots if any(spot.status == 'A' for spot in lot.spots)]

    active_reservation = Reservation.query.filter_by(user_id=current_user.id, leaving_time=None).first()
    edit_form = UserEditForm()
    
    return render_template("user/dashboard.html", lots=lots, active=active_reservation, search=search_text, available_only=available_only, edit_form=edit_form)


@user.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():
    form = UserEditForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        if form.password.data:
            current_user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash("Profile updated!", "success")
    else:
        flash("Error updating profile.", "danger")
    return redirect(url_for('user.dashboard'))


@user.route("/book/<int:lot_id>")
@login_required
def book_spot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if Reservation.query.filter_by(user_id=current_user.id, leaving_time=None).first():
        flash("You already have an active reservation!", "warning")
        return redirect(url_for("user.dashboard"))

    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not available_spot:
        flash("No spots available in this lot.", "danger")
        return redirect(url_for("user.dashboard"))

    reservation = Reservation(
        spot_id=available_spot.id,
        user_id=current_user.id,
        parking_time=datetime.now(),
        cost_per_hour=lot.price_per_hour
    )

    available_spot.status = 'O'
    db.session.add(reservation)
    db.session.commit()
    flash(f"Spot {available_spot.id} booked successfully!", "success")
    return redirect(url_for("user.dashboard"))


@user.route("/release")
@login_required
def release_spot():
    reservation = Reservation.query.filter_by(user_id=current_user.id, leaving_time=None).first()
    if not reservation:
        flash("No active reservation found.", "warning")
        return redirect(url_for("user.dashboard"))

    reservation.leaving_time = datetime.now()

    # Calculate cost (optional for display)
    spot = reservation.spot
    spot.status = 'A'

    db.session.commit()
    flash("Spot released. Thank you!", "info")
    return redirect(url_for("user.dashboard"))


@user.route("/history")
@login_required
def history():
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template("user/history.html", reservations=reservations)
