from flask import Blueprint, request, render_template
import sqlite3

reports_bp = Blueprint('reports', __name__)

report_queries = {
    'most_popular_songs': """
        SELECT Song.SongTitle, AVG(Rating.RatingValue) AS AvgRating
        FROM Song
        LEFT JOIN Rating ON Song.SongID = Rating.SongID
        GROUP BY Song.SongID
        ORDER BY AvgRating DESC
    """,
    'ratings_5_stars': """
        SELECT Song.SongTitle, Rating.RatingValue, Rating.Review 
        FROM Rating 
        INNER JOIN Song ON Rating.SongID = Song.SongID 
        WHERE RatingValue = 5;
    """,
    'vip_event_attendees': """
        SELECT Event.Name AS EventName, User.FirstName, User.LastName 
        FROM EventAttendee 
        INNER JOIN Event ON EventAttendee.EventID = Event.EventID 
        INNER JOIN User ON EventAttendee.UserID = User.UserID 
        WHERE TicketType = 'VIP';
    """,
    'songs_per_genre': """
        SELECT Genre.Name, COUNT(Song.SongID) AS SongCount 
        FROM Genre 
        LEFT JOIN Song ON Genre.GenreID = Song.GenreID 
        GROUP BY Genre.Name;
    """,
    'avg_rating_per_song': """
        SELECT Song.SongTitle, AVG(Rating.RatingValue) AS AvgRating 
        FROM Song 
        LEFT JOIN Rating ON Song.SongID = Rating.SongID 
        GROUP BY Song.SongTitle;
    """,
    'user_rating_details': """
        SELECT User.FirstName, User.LastName, Song.SongTitle, Rating.RatingValue, Rating.Review 
        FROM User 
        INNER JOIN Rating ON User.UserID = Rating.UserID 
        INNER JOIN Song ON Rating.SongID = Song.SongID;
    """,
    'genre_song_details': """
        SELECT Genre.Name AS Genre, Song.SongTitle, Song.SongLength 
        FROM Genre 
        INNER JOIN Song ON Genre.GenreID = Song.GenreID;
    """,
    'song_artist_details': """
        SELECT Song.SongTitle, Artist.StageName 
        FROM SongArtist 
        INNER JOIN Song ON SongArtist.SongID = Song.SongID 
        INNER JOIN Artist ON SongArtist.ArtistID = Artist.ArtistID;
    """,
    'event_venue_details': """
        SELECT Event.Name AS EventName, Venue.VenueName, Venue.VenueCity, Venue.VenueState 
        FROM EventVenue 
        INNER JOIN Event ON EventVenue.EventID = Event.EventID 
        INNER JOIN Venue ON EventVenue.VenueID = Venue.VenueID;
    """,
    'event_attendee_details': """
        SELECT Event.Name AS EventName, User.FirstName, User.LastName, EventAttendee.RegistrationDate, EventAttendee.TicketType 
        FROM EventAttendee 
        INNER JOIN Event ON EventAttendee.EventID = Event.EventID 
        INNER JOIN User ON EventAttendee.UserID = User.UserID;
    """
}

@reports_bp.route('/reports', methods=['GET'])
def reports():
    return render_template('reports.html')

@reports_bp.route('/generate_report', methods=['POST'])
def generate_report():
    report_type = request.form['report_type']
    
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()

    if report_type in report_queries:
        cursor.execute(report_queries[report_type])
        rows = cursor.fetchall()
        headers = [description[0] for description in cursor.description]
        conn.close()
        return render_template('report_results.html', title=report_type.replace('_', ' ').title(), headers=headers, rows=rows)
    else:
        conn.close()
        return render_template('reports.html')
