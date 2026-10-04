# 📄 Resume Analyzer

A Flask web app that reads a PDF resume, extracts the text, identifies technical skills and keywords with NLP, gives a resume score out of 100 and suggests improvements.

## Features

- 📄 Upload a PDF resume (drag and drop supported)
- 🔍 Automatic text extraction
- 🧠 Technical skill detection grouped by category
- 🔑 Top keyword extraction
- 📈 Resume score out of 100 with a score breakdown
- 💡 Personalised suggestions for improvement
- 📋 Copy results button
- Responsive layout with light and dark mode

## How it works

```
Upload Resume (PDF)
        ↓
Extract Resume Text (pypdf)
        ↓
NLP Processing (tokenization, stop-word removal)
        ↓
Identify Skills / Keywords
        ↓
Analyze Resume (rule-based scoring)
        ↓
Display Results
```

## Scoring

| Category | Points |
|----------|--------|
| Contact info and links (email, phone, GitHub / LinkedIn) | 15 |
| Resume sections (education, skills, projects, experience, summary, certifications) | 25 |
| Technical skills detected | 25 |
| Measurable achievements (percentages, numbers) | 15 |
| Action verbs | 10 |
| Length | 10 |

## Example

```
RESUME ANALYSIS

Skills Found:
✓ Python
✓ SQL
✓ HTML
✓ CSS
✓ JavaScript

Keywords:
python • machine • learning • web

Resume Score:
82 / 100

Suggestions:
- Add more measurable project achievements.
- Add a clear 'Experience / Internships' section.
```

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask |
| PDF parsing | pypdf |
| NLP | NLTK |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render, Gunicorn |

## Project structure

```
Resume-Analyzer/
│
├── app.py                 # Flask routes and upload validation
├── resume_analyzer.py     # PDF extraction, NLP, skills, scoring
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── README.md
```

## Run locally

```bash
git clone https://github.com/danyaramesh1647-lang/resume-analyzer.git
cd resume-analyzer
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5050. NLTK downloads the data it needs automatically on the first run.

## API

**POST** `/analyze` with `multipart/form-data` and a PDF in the `resume` field. Returns the score, breakdown, skills, keywords and suggestions as JSON.

## Limitations

- Works only with text-based PDFs, not scanned images.
- Skill detection uses a predefined skill list, so skills outside the list are not detected.
- The score is a rule-based estimate, not a real recruiter or ATS score.
- English resumes only.

## Future improvements

- Job description matching (skill gap analysis)
- DOCX support
- Named entity recognition for names, companies and dates

## Author

**Danya R**
GitHub: [danyaramesh1647-lang](https://github.com/danyaramesh1647-lang)