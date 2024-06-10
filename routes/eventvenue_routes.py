from flask import Blueprint, request
import os
import requests

eventvenues = Blueprint('eventvenues', __name__)

def geocode_address(street, city, state):
    address = f"{street}, {city}, {state}"
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(geocode_url)
    geocode_data = response.json()
    if geocode_data['status'] == 'OK':
        location = geocode_data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None