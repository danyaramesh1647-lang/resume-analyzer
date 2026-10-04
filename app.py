from flask import Flask, jsonify, render_template, request
from resume_analyzer import analyze

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_route():
    file = request.files.get("resume")
    if not file or not file.filename:
        return jsonify({"error": "Choose a PDF resume to upload."}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400
    data = file.read()
    if not data.startswith(b"%PDF"):
        return jsonify({"error": "This file is not a valid PDF."}), 400
    try:
        return jsonify(analyze(data))
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception:
        return jsonify({"error": "Could not read this PDF. Try exporting it again."}), 422


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "File is too large. Keep it under 5 MB."}), 413


if __name__ == "__main__":
    app.run(debug=True, port=5050)