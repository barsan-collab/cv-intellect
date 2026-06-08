import os
import json
import mysql.connector
import pypdf
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash
from cv_engine import parse_cv

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cv_intellect_secret_node_key")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # disable static file caching in dev

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="cv_intellect_db",
        port=3307
    )


def migrate_db():
    """Add new columns to cv_analyses if they don't exist yet."""
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM cv_analyses LIKE 'metadata'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE cv_analyses ADD COLUMN metadata LONGTEXT")
            conn.commit()
            print("[DB] Added 'metadata' column to cv_analyses")
        cursor.close(); conn.close()
    except Exception as e:
        print(f"[DB MIGRATE] {e}")

migrate_db()


def extract_text_from_pdf(file_path):
    extracted_text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] Failed to read PDF: {e}")
    return extracted_text.strip()


# ── Routes ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        role     = request.form.get('role', 'applicant')
        password = request.form.get('password', '')

        if not username or not password:
            flash("Credentials cannot be left empty.")
            return redirect(url_for('register'))

        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash("Username already registered.")
                cursor.close(); conn.close()
                return redirect(url_for('register'))

            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, role)
            )
            conn.commit()
            cursor.close(); conn.close()
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            conn   = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close(); conn.close()

            if user:
                session['user_id']  = user['id']
                session['username'] = user['username']
                session['role']     = user['role']
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password.")
                return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    history = []
    stats   = {'total': 0, 'avg_score': 0, 'top_score': 0}
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cv_analyses ORDER BY id DESC")
        history = cursor.fetchall()

        if history:
            ratings       = [r['hr_rating'] for r in history if r.get('hr_rating')]
            stats['total']     = len(history)
            stats['avg_score'] = round(sum(ratings) / len(ratings), 1) if ratings else 0
            stats['top_score'] = max(ratings) if ratings else 0

        cursor.close(); conn.close()
    except mysql.connector.Error:
        pass

    if session.get('role') == 'hr':
        return render_template('dashboard_hr.html', history=history, stats=stats)
    return render_template('dashboard_applicant.html', history=history, stats=stats)


@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash("No file payload detected.")
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected.")
        return redirect(url_for('dashboard'))

    if not file.filename.lower().endswith('.pdf'):
        flash("Only PDF files are accepted.")
        return redirect(url_for('dashboard'))

    filename  = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    cv_text = extract_text_from_pdf(file_path)
    if not cv_text:
        flash("Could not extract text from the PDF.")
        return redirect(url_for('dashboard'))

    try:
        print("[CV ENGINE] Parsing resume...")
        data = parse_cv(cv_text)
        print(f"[CV ENGINE] Done — {data['name']}, score={data['rating']}")

        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cv_analyses (name, email, phone, hr_rating, hr_verdict, pros, cons, metadata) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                data['name'], data['email'], data['phone'],
                data['rating'], data['verdict'],
                "|".join(data['pros']),
                "|".join(data['cons']),
                json.dumps(data.get('metadata', {})),
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close(); conn.close()

        return redirect(url_for('view_results', analysis_id=new_id))

    except mysql.connector.Error as err:
        flash(f"Database error: {err}")
        return redirect(url_for('dashboard'))
    except Exception as ex:
        flash(f"Parsing error: {ex}")
        return redirect(url_for('dashboard'))


@app.route('/results/<int:analysis_id>')
def view_results(analysis_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cv_analyses WHERE id = %s", (analysis_id,))
        result = cursor.fetchone()
        cursor.close(); conn.close()

        if not result:
            flash("Analysis record not found.")
            return redirect(url_for('dashboard'))

        result['pros_list'] = [p for p in result['pros'].split('|') if p] if result.get('pros') else []
        result['cons_list'] = [c for c in result['cons'].split('|') if c] if result.get('cons') else []
        try:
            result['meta'] = json.loads(result['metadata']) if result.get('metadata') else {}
        except (json.JSONDecodeError, TypeError):
            result['meta'] = {}

        return render_template('results.html', result=result)
    except mysql.connector.Error as err:
        flash(f"Error fetching report: {err}")
        return redirect(url_for('dashboard'))


@app.route('/results')
def results_default():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM cv_analyses ORDER BY id DESC LIMIT 1")
        latest = cursor.fetchone()
        cursor.close(); conn.close()
        if latest:
            return redirect(url_for('view_results', analysis_id=latest['id']))
        flash("No analysis records yet.")
        return redirect(url_for('dashboard'))
    except mysql.connector.Error:
        return redirect(url_for('dashboard'))


@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    entries = []
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cv_analyses ORDER BY hr_rating DESC, id ASC")
        rows = cursor.fetchall()
        cursor.close(); conn.close()

        for i, row in enumerate(rows):
            pros_raw = row.get('pros') or ''
            skills   = [p.strip() for p in pros_raw.split('|') if p.strip()][:3]
            entries.append({**row, 'rank': i + 1, 'skills': skills})
    except mysql.connector.Error:
        pass

    return render_template('leaderboard.html', leaderboard=entries)


@app.route('/compare', methods=['POST'])
def compare():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    ids = request.form.getlist('compare_ids')
    if len(ids) < 2:
        flash("Please select at least 2 candidates to compare.")
        return redirect(url_for('leaderboard'))

    candidates = []
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        for cid in ids[:4]:
            cursor.execute("SELECT * FROM cv_analyses WHERE id = %s", (cid,))
            row = cursor.fetchone()
            if row:
                row['pros_list'] = [p for p in row['pros'].split('|') if p] if row.get('pros') else []
                row['cons_list'] = [c for c in row['cons'].split('|') if c] if row.get('cons') else []
                candidates.append(row)
        cursor.close(); conn.close()
    except mysql.connector.Error:
        pass

    if len(candidates) < 2:
        flash("Could not load enough candidates for comparison.")
        return redirect(url_for('leaderboard'))

    return render_template('compare.html', candidates=candidates)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
