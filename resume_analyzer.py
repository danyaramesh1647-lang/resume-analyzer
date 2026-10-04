"""Resume analyzer: PDF text extraction + NLP preprocessing (NLTK) +
skill/keyword identification + rule-based scoring and suggestions."""
import re
from collections import Counter
from io import BytesIO

import nltk
from pypdf import PdfReader

for pkg in ("punkt", "punkt_tab", "stopwords"):
    try:
        nltk.data.find(("corpora/" if pkg == "stopwords" else "tokenizers/") + pkg)
    except LookupError:
        nltk.download(pkg, quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

STOP_WORDS = set(stopwords.words("english"))

# skill -> list of spellings to look for
SKILLS = {
    "Programming Languages": {
        "Python": ["python"], "Java": ["java"], "JavaScript": ["javascript"],
        "TypeScript": ["typescript"], "C++": ["c++"], "C#": ["c#"],
        "PHP": ["php"], "Kotlin": ["kotlin"], "SQL": ["sql"], "C": ["C"],
    },
    "Web Development": {
        "HTML": ["html", "html5"], "CSS": ["css", "css3"],
        "React": ["react", "reactjs", "react.js"], "Angular": ["angular"],
        "Node.js": ["node.js", "nodejs"], "Express": ["express", "express.js"],
        "Flask": ["flask"], "Django": ["django"], "Bootstrap": ["bootstrap"],
        "Tailwind CSS": ["tailwind", "tailwind css"], "REST API": ["rest api", "restful", "rest apis"],
    },
    "Databases": {
        "MySQL": ["mysql"], "PostgreSQL": ["postgresql", "postgres"],
        "MongoDB": ["mongodb"], "SQLite": ["sqlite"], "Firebase": ["firebase"],
        "Oracle": ["oracle"],
    },
    "Data Science and AI": {
        "Machine Learning": ["machine learning"], "Deep Learning": ["deep learning"],
        "NLP": ["nlp", "natural language processing"], "NumPy": ["numpy"],
        "Pandas": ["pandas"], "Scikit-learn": ["scikit-learn", "sklearn"],
        "TensorFlow": ["tensorflow"], "Keras": ["keras"], "PyTorch": ["pytorch"],
        "OpenCV": ["opencv"], "NLTK": ["nltk"], "Matplotlib": ["matplotlib"],
        "Data Analysis": ["data analysis", "data analytics"],
    },
    "Tools and Cloud": {
        "Git": ["git"], "GitHub": ["github"], "Docker": ["docker"], "AWS": ["aws"],
        "Azure": ["azure"], "Linux": ["linux"], "Postman": ["postman"],
        "Render": ["render"], "Figma": ["figma"], "VS Code": ["vs code", "vscode"],
    },
    "CS Fundamentals": {
        "Data Structures": ["data structures"], "Algorithms": ["algorithms"],
        "OOP": ["oop", "object oriented", "object-oriented"], "DBMS": ["dbms"],
        "Operating Systems": ["operating systems"], "Computer Networks": ["computer networks"],
    },
}

SECTIONS = {
    "Education": (r"\beducation\b|\bacademic\b", 5),
    "Skills": (r"\bskills\b|\btechnical skills\b", 5),
    "Projects": (r"\bprojects?\b", 6),
    "Experience / Internships": (r"\bexperience\b|\binternships?\b", 4),
    "Summary / Objective": (r"\bsummary\b|\bobjective\b|\bprofile\b|\babout me\b", 3),
    "Certifications": (r"\bcertifications?\b|\bcertificates?\b|\bcourses?\b", 2),
}

ACTION_VERBS = ["built", "developed", "designed", "implemented", "created", "deployed",
                "analyzed", "optimized", "integrated", "led", "improved", "automated",
                "collaborated", "managed", "tested", "engineered", "launched", "trained"]

NOISE = {"resume", "email", "phone", "gmail", "com", "linkedin", "github", "https", "http",
         "www", "using", "used", "also", "based", "like", "well", "good", "new", "etc"}


def extract_text(file_bytes):
    reader = PdfReader(BytesIO(file_bytes))
    pages = [(p.extract_text() or "") for p in reader.pages]
    return "\n".join(pages), len(reader.pages)


def _has(text, lower, term):
    if term == "C":  # single letter: case-sensitive
        return re.search(r"(?<![A-Za-z0-9+#])C(?![A-Za-z0-9+#])", text) is not None
    pat = r"(?<![a-z0-9+#])" + re.escape(term) + r"(?![a-z0-9+#])"
    return re.search(pat, lower) is not None


def find_skills(text):
    lower = text.lower()
    found = {}
    for category, skills in SKILLS.items():
        hits = [name for name, aliases in skills.items()
                if any(_has(text, lower, a) for a in aliases)]
        if hits:
            found[category] = hits
    return found


def find_keywords(text, limit=8):
    words = [w.lower() for w in word_tokenize(text)]
    words = [w for w in words if w.isalpha() and len(w) > 2
             and w not in STOP_WORDS and w not in NOISE]
    return [w for w, _ in Counter(words).most_common(limit)]


def analyze(file_bytes):
    text, pages = extract_text(file_bytes)
    text = text.strip()
    if len(text.split()) < 30:
        raise ValueError("Could not read text from this PDF. It may be a scanned image. "
                         "Upload a text-based PDF (export it from Word or Google Docs).")

    lower = text.lower()
    words = len(text.split())
    skills = find_skills(text)
    skill_count = sum(len(v) for v in skills.values())
    breakdown, suggestions = [], []

    # 1. Contact and links (15)
    has_email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text) is not None
    has_phone = re.search(r"(\+?\d[\d\s-]{8,}\d)", text) is not None
    has_link = "linkedin.com" in lower or "github.com" in lower
    contact = 5 * has_email + 5 * has_phone + 5 * has_link
    breakdown.append(("Contact and links", contact, 15))
    if not has_email: suggestions.append("Add a professional email address at the top.")
    if not has_phone: suggestions.append("Add a phone number so recruiters can reach you.")
    if not has_link: suggestions.append("Add your GitHub and LinkedIn links.")

    # 2. Sections (25)
    sec_score, found_sec, missing_sec = 0, [], []
    for name, (pattern, pts) in SECTIONS.items():
        if re.search(pattern, lower):
            sec_score += pts
            found_sec.append(name)
        else:
            missing_sec.append(name)
    breakdown.append(("Resume sections", sec_score, 25))
    for name in missing_sec:
        if name == "Certifications":
            suggestions.append("Add certifications or online courses if you have any.")
        elif name == "Summary / Objective":
            suggestions.append("Add a 2 to 3 line summary at the top.")
        else:
            suggestions.append(f"Add a clear '{name}' section.")

    # 3. Skills (25)
    skill_score = round(min(skill_count, 12) / 12 * 25)
    breakdown.append(("Technical skills", skill_score, 25))
    if skill_count < 8:
        suggestions.append("Include more relevant technical skills (languages, tools, frameworks).")
    if "Tools and Cloud" not in skills:
        suggestions.append("Mention tools such as Git, GitHub or Docker.")

    # 4. Measurable achievements (15)
    metrics = (len(re.findall(r"\d+(?:\.\d+)?\s*%", text))
               + len(re.findall(r"\b\d+\+?\s+(?:users|students|records|requests|projects|features|apis?|pages|tests|datasets|models)\b", lower)))
    ach_score = round(min(metrics, 4) / 4 * 15)
    breakdown.append(("Measurable achievements", ach_score, 15))
    if metrics < 3:
        suggestions.append("Add more measurable project achievements (for example: 'reduced load time by 30%').")

    # 5. Action verbs (10)
    verbs = [v for v in ACTION_VERBS if re.search(r"\b" + v + r"\b", lower)]
    verb_score = round(min(len(verbs), 6) / 6 * 10)
    breakdown.append(("Action verbs", verb_score, 10))
    if len(verbs) < 4:
        suggestions.append("Start bullet points with action verbs like built, developed, deployed or optimized.")

    # 6. Length (10)
    if 250 <= words <= 700: length_score = 10
    elif 150 <= words < 250 or 700 < words <= 900: length_score = 6
    else: length_score = 3
    breakdown.append(("Length", length_score, 10))
    if words < 250: suggestions.append("Your resume is short. Add more detail about projects and skills.")
    if words > 700: suggestions.append("Your resume is long. Keep it to one page for internships.")

    score = sum(b[1] for b in breakdown)
    if not suggestions:
        suggestions.append("Great structure. Tailor the keywords to each job description before applying.")

    return {
        "score": score,
        "breakdown": [{"name": n, "got": g, "max": m} for n, g, m in breakdown],
        "skills": skills,
        "skill_count": skill_count,
        "keywords": find_keywords(text),
        "sections_found": found_sec,
        "sections_missing": missing_sec,
        "suggestions": suggestions[:6],
        "stats": {"words": words, "pages": pages},
    }