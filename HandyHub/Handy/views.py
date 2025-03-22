from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
# from .models import Note
from . import db
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .models import Provider, Service,User,Booking
import uuid



views = Blueprint('views', __name__)


UPLOAD_FOLDER = 'static/uploads/providers'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@views.route('/')
def home():
    return render_template("index.html")

@views.route('/about')
def about():
    return render_template("about.html")

@views.route('/services')
def services():
    return render_template("services.html")

@views.route('/contact')
def contact():
    return render_template("contact.html")

@views.route('/handyman')
def handyman():
    services = Service.query.all()  # Fetch all services
    providers_by_service = {service.id: [] for service in services}  # Create a dictionary to hold providers by service

    # Fetch all providers and group them by service
    providers = Provider.query.all()
    for provider in providers:
        providers_by_service[provider.service_id].append(provider)

    return render_template("handyman.html",  services=services, providers_by_service=providers_by_service)

# Ensure correct path to static folder
# Ensure correct path to static folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get project root
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'providers')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/profile-provider', methods=['GET', 'POST'])
@login_required
def provider_profile():
    provider = Provider.query.filter_by(id=current_user.id).first()

    if request.method == 'POST':
        provider.first_name = request.form.get('first_name')
        provider.last_name = request.form.get('last_name')
        provider.business_name = request.form.get('business_name')
        provider.service_id = request.form.get('service_id')
        provider.service_price = request.form.get('service_price')
        provider.experience = request.form.get('experience')
        provider.location = request.form.get('location')

        # Handle image upload
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Generate a unique filename
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"  # Unique filename
                
                # Delete old image if it exists
                if provider.image:
                    old_image_path = os.path.join(UPLOAD_FOLDER, provider.image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # Save the new file
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Store only the filename in DB
                provider.image = filename  

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('views.provider_profile'))

    services = Service.query.all()  # Get all services for dropdown
    return render_template('provider_profile.html', provider=provider, services=services)

@views.route('/profile-customer', methods=['GET', 'POST'])
@login_required
def customer_profile():
    if request.method == 'POST':
        # Update Profile Fields
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')

        # Handle Profile Picture Upload
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Generate a unique filename
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"  # Unique filename
                
                # Delete old image if it exists
                if current_user.image and current_user.image != "default.png":
                    old_image_path = os.path.join(UPLOAD_FOLDER, current_user.image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # Save the new file
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                # Store only the filename in DB
                current_user.image = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('views.customer_profile'))  # Fix function reference

    return render_template('customer_profile.html', user=current_user)






@views.route('/provider/<int:provider_id>', methods=['GET'])
@login_required
def provider_details(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    return render_template('provider_details.html', provider=provider)

@views.route('/book/<int:provider_id>', methods=['POST'])
@login_required
def book_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')

    if not booking_date or not booking_time:
        flash("Please select both date and time.", "danger")
        return redirect(url_for('views.provider_details', provider_id=provider.id))

    # Save to database
    new_booking = Booking(
        customer_id=current_user.id,
        provider_id=provider.id,
        service_id=provider.service_id,
        booking_date=datetime.strptime(booking_date, "%Y-%m-%d"),
        booking_time=datetime.strptime(booking_time, "%H:%M").time(),
        status="Pending"
    )

    db.session.add(new_booking)
    db.session.commit()
    print("Booking successful! Your request is pending confirmation.")
    
    flash("Booking successful! Your request is pending confirmation.", "success")
    return redirect(url_for('views.booking_history'))


@views.route('/booking-history')
@login_required
def booking_history():
    bookings = Booking.query.filter_by(customer_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('booking_history.html', bookings=bookings)


@views.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.customer_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('booking_history'))

    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        db.session.commit()
        flash('Booking has been cancelled successfully.', 'success')
    else:
        flash('Booking cannot be cancelled.', 'warning')

    return redirect(url_for('views.booking_history'))


@views.route('/provider-bookings')
@login_required
def provider_bookings():

    bookings = Booking.query.filter_by(provider_id=current_user.id).order_by(Booking.created_at.desc()).all()
    
    return render_template('provider_bookings.html', bookings=bookings)


@views.route('/confirm-booking/<int:booking_id>', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if provider owns the booking
    if booking.provider_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('views.provider_bookings'))

    if booking.status == "Pending":
        booking.status = "Confirmed"
        db.session.commit()
        flash("Booking confirmed successfully!", "success")
    else:
        flash("Only pending bookings can be confirmed.", "warning")

    return redirect(url_for('views.provider_bookings'))


@views.route('/reject-booking/<int:booking_id>', methods=['POST'])
@login_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if provider owns the booking
    if booking.provider_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('views.provider_bookings'))

    if booking.status == "Pending":
        booking.status = "Rejected"
        db.session.commit()
        flash("Booking rejected successfully!", "success")
    else:
        flash("Only pending bookings can be rejected.", "warning")

    return redirect(url_for('views.provider_bookings'))


@views.route('/complete-booking/<int:booking_id>', methods=['POST'])
@login_required
def complete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if the provider owns this booking
    if booking.provider_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('views.provider_bookings'))

    if booking.status == "Confirmed":
        booking.status = "Completed"
        db.session.commit()
        flash("Booking marked as completed!", "success")
    else:
        flash("Only confirmed bookings can be marked as completed.", "warning")

    return redirect(url_for('views.provider_bookings'))

