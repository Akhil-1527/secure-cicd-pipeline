from app.app import create_app


def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_health():
    resp = client().get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_add_and_list_note():
    c = client()
    resp = c.post("/notes", json={"text": "hello"})
    assert resp.status_code == 201
    assert resp.get_json()["text"] == "hello"
    listing = c.get("/notes").get_json()["notes"]
    assert any(n["text"] == "hello" for n in listing)


def test_empty_note_rejected():
    resp = client().post("/notes", json={"text": "  "})
    assert resp.status_code == 400
