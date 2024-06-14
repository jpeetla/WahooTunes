from flask import Blueprint, jsonify
import sqlite3
import os
import requests
from urllib.parse import quote

eventvenues = Blueprint('eventvenues', __name__)

def geocode_address(street, city, state):
    address = f"{street}, {city}, {state}"
    encoded_address = quote(address)
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
    #print(geocode_url)
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

            # Prepare location data for geocoding
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
        return jsonify([])  # Return empty list in case of error

