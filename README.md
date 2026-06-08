# CV Intellect

An AI-powered resume analysis web app built with Flask. Upload any PDF resume and get a multi-dimensional score, role archetype classification, skill breakdown, red flags, and actionable recommendations — instantly.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.x-orange?style=flat-square&logo=mysql)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Features

- **Deep CV Parsing** — Extracts 40+ fields: name, email, phone, job title, companies, education, skills, certifications, languages, GPA, and more
- **Multi-Dimensional Scoring** — Five independent scores (Skills, Experience, Presentation, Impact, ATS Compatibility) plus an overall rating out of 10
- **Archetype Detection** — Classifies candidates into roles: Software Engineer, Data Scientist, Finance Professional, DevOps Engineer, and more
- **Seniority Detection** — Automatically infers level (Junior / Mid-Level / Senior / Director / Executive)
- **Red Flags & Recommendations** — Surfaces issues and suggests concrete improvements
- **Talent Leaderboard** — All candidates ranked by AI score with live search
- **Side-by-Side Comparison** — Compare 2–4 candidates across all dimensions
- **Role-Based Portals** — Separate dashboards for Applicants and HR Recruiters
- **Apple-inspired UI** — True black glassmorphism design with smooth animations

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | MySQL (via XAMPP on port 3307) |
| PDF Parsing | pypdf |
| CV Analysis | Custom rule-based NLP engine (`cv_engine.py`) |
| Frontend | Jinja2, vanilla JS, CSS (glassmorphism) |
| Fonts | Inter (Google Fonts) + Font Awesome 6 |

---

## Getting Started

### Prerequisites

- Python 3.10+
- [XAMPP](https://www.apachefriends.org/) with MySQL running on port **3307**
- pip

### Installation

```bash
git clone https://github.com/barsan-collab/cv-intellect.git
cd cv-intellect
pip install flask pypdf mysql-connector-python werkzeug
```

### Database Setup

1. Start XAMPP and ensure **MySQL** is running
2. Open phpMyAdmin (`http://localhost/phpmyadmin`)
3. Create a database named `cv_intellect_db`
4. Run the following SQL:

```sql
CREATE DATABASE IF NOT EXISTS cv_intellect_db;
USE cv_intellect_db;

CREATE TABLE users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80)  NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    role     VARCHAR(20)  NOT NULL DEFAULT 'applicant'
);

CREATE TABLE cv_analyses (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(200),
    email      VARCHAR(200),
    phone      VARCHAR(50),
    hr_rating  INT,
    hr_verdict TEXT,
    pros       TEXT,
    cons       TEXT,
    metadata   LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Run

```bash
python app.py
```

Open `http://127.0.0.1:5001` in your browser.

---

## Project Structure

```
cv-intellect/
├── app.py              # Flask routes and DB logic
├── cv_engine.py        # AI parsing and scoring engine
├── static/
│   └── css/
│       └── main.css    # Design system (Apple-inspired)
├── templates/
│   ├── index.html          # Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard_applicant.html
│   ├── dashboard_hr.html
│   ├── results.html        # Analysis report
│   ├── leaderboard.html
│   └── compare.html
├── uploads/            # Uploaded PDFs (git-ignored)
└── resources/          # Sample resumes (git-ignored)
```

---

## How the CV Engine Works

`cv_engine.py` is a rule-based NLP engine — no external AI API required.

1. **Text extraction** — pypdf pulls raw text from the PDF
2. **Field extraction** — Regex + heuristics identify name, email, phone, job title, companies, dates, education
3. **Skill mapping** — 200+ skills across 8 categories matched against the text
4. **Scoring** — Five dimension scores computed from skill depth, experience years, formatting signals, and keyword density
5. **Archetype detection** — Weighted skill-category scores determine the best-fit role
6. **Seniority inference** — Title keywords + years of experience → seniority level
7. **Red flags** — Checks for missing contact info, short experience, lack of quantified achievements, etc.
8. **Recommendations** — Generated based on detected weaknesses

---

## Screenshots

| Landing Page | Dashboard | Results |
|---|---|---|
| Apple-style hero with stats | Upload + candidate history | Score gauge, skill tags, recommendations |

---

## License

MIT
