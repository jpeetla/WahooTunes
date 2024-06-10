from flask import Blueprint, request, render_template
import sqlite3

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['GET'])
def reports():
    return render_template('reports.html')

@reports_bp.route('/generate_report', methods=['POST'])
def generate_report():
    report_type = request.form['report_type']
    
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()

    if report_type == 'most_popular_songs':
        cursor.execute("""
            SELECT Song.SongTitle, AVG(Rating.RatingValue) AS AvgRating
            FROM Song
            LEFT JOIN Rating ON Song.SongID = Rating.SongID
            GROUP BY Song.SongID
            ORDER BY AvgRating DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return render_template('most_popular_songs.html', results=results)
    else: 
        return render_template('reports.html')