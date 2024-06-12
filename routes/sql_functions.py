import sqlite3
import os
import requests

def get_songs():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT Song.SongID, Song.SongTitle, Artist.StageName FROM Song JOIN SongArtist ON Song.SongID = SongArtist.SongID JOIN Artist ON SongArtist.ArtistID = Artist.ArtistID")
    songs = cursor.fetchall()
    conn.close()
    return songs

def get_song_details(song_id):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SongID, SongTitle, GenreID, 
               (SELECT Name FROM Genre WHERE GenreID = Song.GenreID) as Genre, 
               (SELECT StageName FROM Artist WHERE ArtistID = (SELECT ArtistID FROM SongArtist WHERE SongID = ?)) as Artist, 
               SongLength, 
               (SELECT ArtistID FROM Artist WHERE ArtistID = (SELECT ArtistID FROM SongArtist WHERE SongID = ?)) as ArtistID
        FROM Song 
        WHERE SongID = ?""", (song_id, song_id, song_id))
    song = cursor.fetchone()
    cursor.execute("SELECT RatingValue, Review, (SELECT Email FROM User WHERE UserID = Rating.UserID) as User FROM Rating WHERE SongID = ?", (song_id,))
    ratings = cursor.fetchall()
    conn.close()
    return song, ratings

def get_artists():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT ArtistID, StageName FROM Artist")
    artists = cursor.fetchall()
    conn.close()
    return artists

def get_artist_details(artist_id):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT StageName, RealName, PhoneNumber FROM Artist WHERE ArtistID = ?", (artist_id,))
    artist = cursor.fetchone()
    cursor.execute("""
        SELECT Song.SongID, Song.SongTitle, IFNULL(AVG(Rating.RatingValue), 'No ratings yet') as AvgRating
        FROM Song
        JOIN SongArtist ON Song.SongID = SongArtist.SongID
        LEFT JOIN Rating ON Song.SongID = Rating.SongID
        WHERE SongArtist.ArtistID = ?
        GROUP BY Song.SongID
    """, (artist_id,))
    songs = cursor.fetchall()
    conn.close()
    return artist, songs

def get_genres():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT GenreID, Name FROM Genre")
    genres = cursor.fetchall()
    conn.close()
    return genres

def get_genre_details(genre_id):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM Genre WHERE GenreID = ?", (genre_id,))
    genre = cursor.fetchone()
    cursor.execute("""
        SELECT Song.SongID, Song.SongTitle, IFNULL(AVG(Rating.RatingValue), 'No ratings yet') as AvgRating, Artist.ArtistID, Artist.StageName
        FROM Song
        LEFT JOIN Rating ON Song.SongID = Rating.SongID
        JOIN SongArtist ON Song.SongID = SongArtist.SongID
        JOIN Artist ON SongArtist.ArtistID = Artist.ArtistID
        WHERE Song.GenreID = ?
        GROUP BY Song.SongID, Song.SongTitle
    """, (genre_id,))
    songs = cursor.fetchall()
    conn.close()
    return genre, songs

def get_user_id(user_email):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT UserID FROM User WHERE Email = ?", (user_email,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

def has_user_rated_song(user_id, song_id):
        conn = sqlite3.connect('music.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Rating WHERE UserID = ? AND SongID = ?", (user_id, song_id))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

def get_user_ratings(user_email):
    user_id = get_user_id(user_email)
    if not user_id:
        return []
    
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Rating.RatingValue, Rating.Review, Song.SongTitle, Artist.StageName, Song.SongID, Artist.ArtistID
        FROM Rating
        JOIN Song ON Rating.SongID = Song.SongID
        JOIN SongArtist ON Song.SongID = SongArtist.SongID
        JOIN Artist ON SongArtist.ArtistID = Artist.ArtistID
        WHERE Rating.UserID = ?
    """, (user_id,))
    user_ratings = cursor.fetchall()
    conn.close()
    return user_ratings

def get_venues():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT VenueName, VenueStreet, VenueCity, VenueState FROM Venue')
    venues = cursor.fetchall()
    conn.close()
    return venues

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

def get_ratings_with_5_stars():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Song.SongTitle, Rating.RatingValue, Rating.Review 
    FROM Rating 
    INNER JOIN Song ON Rating.SongID = Song.SongID 
    WHERE RatingValue = 5;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_vip_event_attendees():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Event.Name AS EventName, User.FirstName, User.LastName 
    FROM EventAttendee 
    INNER JOIN Event ON EventAttendee.EventID = Event.EventID 
    INNER JOIN User ON EventAttendee.UserID = User.UserID 
    WHERE TicketType = 'VIP';
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_songs_per_genre():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Genre.Name, COUNT(Song.SongID) AS SongCount 
    FROM Genre 
    LEFT JOIN Song ON Genre.GenreID = Song.GenreID 
    GROUP BY Genre.Name;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_avg_rating_per_song():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Song.SongTitle, AVG(Rating.RatingValue) AS AvgRating 
    FROM Song 
    LEFT JOIN Rating ON Song.SongID = Rating.SongID 
    GROUP BY Song.SongTitle;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_user_rating_details():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT User.FirstName, User.LastName, Song.SongTitle, Rating.RatingValue, Rating.Review 
    FROM User 
    INNER JOIN Rating ON User.UserID = Rating.UserID 
    INNER JOIN Song ON Rating.SongID = Song.SongID;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_genre_song_details():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Genre.Name AS Genre, Song.SongTitle, Song.SongLength 
    FROM Genre 
    INNER JOIN Song ON Genre.GenreID = Song.GenreID;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_song_artist_details():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Song.SongTitle, Artist.StageName 
    FROM SongArtist 
    INNER JOIN Song ON SongArtist.SongID = Song.SongID 
    INNER JOIN Artist ON SongArtist.ArtistID = Artist.ArtistID;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_event_venue_details():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Event.Name AS EventName, Venue.VenueName, Venue.VenueCity, Venue.VenueState 
    FROM EventVenue 
    INNER JOIN Event ON EventVenue.EventID = Event.EventID 
    INNER JOIN Venue ON EventVenue.VenueID = Venue.VenueID;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def get_event_attendee_details():
    conn = sqlite3.connect('music.sqlite3')
    query = """
    SELECT Event.Name AS EventName, User.FirstName, User.LastName, EventAttendee.RegistrationDate, EventAttendee.TicketType 
    FROM EventAttendee 
    INNER JOIN Event ON EventAttendee.EventID = Event.EventID 
    INNER JOIN User ON EventAttendee.UserID = User.UserID;
    """
    result = conn.execute(query).fetchall()
    conn.close()
    return result
