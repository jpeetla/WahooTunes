from flask import Blueprint, jsonify, render_template, request, session, redirect, flash
import sqlite3
import os
import requests
from urllib.parse import quote
import sqlite3
import datetime
from .sql_functions import get_user_reg

eventvenues = Blueprint('eventvenues', __name__)

def geocode_address(street, city, state):
    address = f"{street}, {city}, {state}"
    encoded_address = quote(address)
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
    response = requests.get(geocode_url)
    geocode_data = response.json()
    if geocode_data['status'] == 'OK':
        location = geocode_data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None

@eventvenues.route('/venues')
def get_venues():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT
                v.VenueID,
                v.VenueName,
                v.VenueStreet,
                v.VenueCity,
                v.VenueState,
                v.VenueZipCode,
                v.VenueWebsite,
                v.ContactFirstName,
                v.ContactLastName,
                v.PhoneNumber,
                ev.EventID,
                e.Name AS EventName,
                e.Date AS EventDate,
                e.ContactFirstName AS EventContactFirstName,
                e.ContactLastName AS EventContactLastName,
                e.CPPhoneNumber AS EventPhoneNumber
            FROM
                Venue v
            LEFT JOIN
                EventVenue ev ON v.VenueID = ev.VenueID
            LEFT JOIN
                Event e ON ev.EventID = e.EventID
            ORDER BY
                v.VenueID, e.Date
        ''')

        venues = cursor.fetchall()
        conn.close()

        venue_data = []
        for venue in venues:
            venue_id, venue_name, street, city, state, zipcode, website, \
                contact_first_name, contact_last_name, phone_number, \
                event_id, event_name, event_date, event_contact_first_name, \
                event_contact_last_name, event_phone_number = venue

            lat, lng = geocode_address(street, city, state)
            if lat and lng:
                venue_info = {
                    'lat': lat,
                    'lng': lng,
                    'info': f'{venue_name}<br>Event: {event_name}<br>Date: {event_date}'
                }
                venue_data.append(venue_info)

        return jsonify(venue_data)

    except sqlite3.Error as e:
        print("Error fetching venue data:", e)
        conn.close()
        return jsonify([])

def get_events():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT
                EventID,
                Name,
                Date,
                ContactFirstName,
                ContactLastName,
                CPPhoneNumber
            FROM
                Event
            ORDER BY
                Date
        ''')

        events = cursor.fetchall()
        conn.close()

        event_data = []
        for event in events:
            event_id, name, date, contact_first_name, contact_last_name, phone_number = event
            event_info = {
                'event_id': event_id,
                'name': name,
                'date': date,
                'contact_first_name': contact_first_name,
                'contact_last_name': contact_last_name,
                'phone_number': phone_number
            }
            event_data.append(event_info)

        return event_data

    except sqlite3.Error as e:
        print("Error fetching event data:", e)
        conn.close()
        return []

@eventvenues.route('/events', methods=['POST'])
def register_event():
    if request.method == 'POST':
        if 'user' not in session:
            flash('Please log in to register for events.', 'error')
            return redirect('/events')  # Redirect to events page if user not logged in

        user_email = session['user']
        event_id = request.form['event_id']
        ticket_type = request.form['ticket_type']

        try:
            conn = sqlite3.connect('music.sqlite3')
            cursor = conn.cursor()

            # Retrieve user details from database based on email
            cursor.execute("SELECT UserID FROM User WHERE Email = ?", (user_email,))
            user_record = cursor.fetchone()

            if not user_record:
                flash('User not found. Please contact support.', 'error')
                return redirect('/events')

            user_id = user_record[0]

            # Check if the user has already registered for the event
            cursor.execute("SELECT COUNT(*) FROM EventAttendee WHERE EventID = ? AND UserID = ?", (event_id, user_id))
            existing_registration = cursor.fetchone()[0]

            if existing_registration > 0:
                flash('You have already registered for this event.', 'warning')
                return redirect('/events')

            # Insert into EventAttendee table
            registration_date = datetime.date.today().isoformat()
            insert_attendee_sql = """
            INSERT INTO EventAttendee (RegistrationDate, TicketType, EventID, UserID)
            VALUES (?, ?, ?, ?);
            """
            cursor.execute(insert_attendee_sql, (registration_date, ticket_type, event_id, user_id))
            conn.commit()
            conn.close()

            flash('Registration successful!', 'success')
            return redirect('/events')  # Redirect to events page after successful registration

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            flash(f'Registration failed. Error: {str(e)}', 'error')
            return redirect('/events')  # Redirect to events page with error message

    flash('Method not allowed.', 'error')
    return redirect('/events')


@eventvenues.route('/events')
def events():
    # Check if user is logged in
    if 'user' not in session:
        return jsonify({'error': 'User not logged in.'}), 401

    try:
        user_email = session['user']
        conn = sqlite3.connect('music.sqlite3')
        cursor = conn.cursor()

        # Fetch user details
        cursor.execute("SELECT FirstName, LastName FROM User WHERE Email = ?", (user_email,))
        user_details = cursor.fetchone()

        if not user_details:
            return jsonify({'error': 'User not found.'}), 404

        user_first_name, user_last_name = user_details

        # Fetch events data
        cursor.execute('''
            SELECT
                EventID,
                Name,
                Date,
                ContactFirstName,
                ContactLastName,
                CPPhoneNumber
            FROM
                Event
            ORDER BY
                Date
        ''')

        events = cursor.fetchall()
        conn.close()

        event_data = []
        for event in events:
            event_id, name, date, contact_first_name, contact_last_name, phone_number = event
            event_info = {
                'event_id': event_id,
                'name': name,
                'date': date,
                'contact_first_name': contact_first_name,
                'contact_last_name': contact_last_name,
                'phone_number': phone_number,
                'user_first_name': user_first_name,
                'user_last_name': user_last_name,
                'email': user_email  # Assuming email is fetched from session
            }
            event_data.append(event_info)

        return render_template('events.html', events=event_data, user_first_name=user_first_name, user_last_name=user_last_name, email=user_email)

    except sqlite3.Error as e:
        print("Error fetching event data:", e)
        conn.close()
        return jsonify({'error': 'Database error.'}), 500

@eventvenues.route('/my_registrations')
def my_registrations():
    if 'user' not in session:
        return render_template('login.html')
    
    user_registrations = get_user_reg(session['user'])
    print(user_registrations)
    events_data = get_events()
    
    return render_template('my_registrations.html', user_registrations=user_registrations, events=events_data)

