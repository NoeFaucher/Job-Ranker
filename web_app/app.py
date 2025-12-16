from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import json

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('../data/jobs.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

def get_available_dates():
    """Récupère toutes les dates disponibles dans la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT inserted_at FROM jobs ORDER BY inserted_at DESC')
    dates = [row['inserted_at'] for row in cursor.fetchall()]
    conn.close()
    return dates

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dates')
def api_dates():
    """API pour récupérer les dates disponibles"""
    dates = get_available_dates()
    return jsonify(dates)

@app.route('/api/jobs')
def api_jobs():
    """API pour récupérer les offres d'emploi filtrées par date et type"""
    date = request.args.get('date')
    include_internships = request.args.get('include_internships', 'false').lower() == 'true'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"Include internships: {include_internships}")
    
    # Construire le filtre pour les stages
    internship_filter = "AND (job_type IS NULL OR job_type NOT LIKE '%internship%')" if not include_internships else ""
    
    if date:
        cursor.execute(f'''
            SELECT id, title, company, location, ai_score, description, 
                   job_url, job_url_direct, date_posted, job_type, 
                   company_logo, inserted_at, ai_skills_required
            FROM jobs 
            WHERE inserted_at = ? and ai_score IS NOT NULL
            {internship_filter}
            ORDER BY ai_score ASC
        ''', (date,))
    else:
        # Si pas de date, prendre la date la plus récente
        cursor.execute(f'''
            SELECT id, title, company, location, ai_score, description, 
                   job_url, job_url_direct, date_posted, job_type, 
                   company_logo, inserted_at, ai_skills_required
            FROM jobs 
            WHERE inserted_at = (SELECT MAX(inserted_at) FROM jobs) and ai_score IS NOT NULL
            {internship_filter}
            ORDER BY ai_score ASC
        ''')
    
    jobs = []
    for row in cursor.fetchall():
        jobs.append({
            'id': row['id'],
            'title': row['title'],
            'company': row['company'],
            'location': row['location'],
            'ai_score': row['ai_score'],
            'description': row['description'],
            'job_url': row['job_url'],
            'job_url_direct': row['job_url_direct'],
            'date_posted': row['date_posted'],
            'job_type': row['job_type'],
            'company_logo': row['company_logo'],
            'inserted_at': row['inserted_at'],
            'ai_skills_required': row['ai_skills_required']
        })
    
    conn.close()
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
