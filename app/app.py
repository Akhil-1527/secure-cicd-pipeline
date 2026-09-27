"""Minimal Flask API used as the target application for the security pipeline.

Kept deliberately small and clean so the pipeline stays green; the point of the
repo is the gates in .github/workflows/security.yml, not the app.
"""
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

_notes = []


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/notes")
def list_notes():
    return jsonify(notes=_notes)


@app.post("/notes")
def add_note():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    if not text:
        return jsonify(error="text is required"), 400
    if len(text) > 280:
        return jsonify(error="text too long"), 400
    note = {"id": len(_notes) + 1, "text": text}
    _notes.append(note)
    return jsonify(note), 201


def create_app():
    return app


if __name__ == "__main__":
    # Local dev only; production runs under gunicorn (see Dockerfile).
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")))
