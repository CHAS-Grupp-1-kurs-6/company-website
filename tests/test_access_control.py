import pytest
from werkzeug.security import generate_password_hash

from company_website import create_app
from company_website.config import Config
from company_website.db import get_db

PASSWORD = "Test-Passw0rd!"


@pytest.fixture
def app(tmp_path, monkeypatch):
    # Egen tillfällig databas, den riktiga datan påverkas inte
    monkeypatch.setattr(Config, "DATABASE", str(tmp_path / "test.db"))
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        conn = get_db()
        for name, notes in [("alice_test", "Alice hemlig anteckning"),
                            ("bob_test", "Bob hemlig anteckning")]:
            conn.execute(
                "INSERT INTO users (username, password_hash, first_name, role, internal_notes, enabled) "
                "VALUES (?, ?, ?, 'employee', ?, 1)",
                (name, generate_password_hash(PASSWORD, method="pbkdf2:sha256"), name, notes),
            )
        conn.commit()
        ids = {r["username"]: r["id"] for r in
               conn.execute("SELECT id, username FROM users WHERE username LIKE '%_test'")}
        conn.close()
    app.test_ids = ids
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username):
    return client.post("/login", data={"username": username, "password": PASSWORD})


def test_kan_inte_redigera_annans_profil(app, client):
    login(client, "alice_test")
    bob = app.test_ids["bob_test"]
    assert client.get(f"/profiles/{bob}/edit").status_code == 403
    assert client.post(f"/profiles/{bob}/edit", data={"first_name": "Hackad"}).status_code == 403


def test_kan_redigera_egen_profil(app, client):
    login(client, "alice_test")
    alice = app.test_ids["alice_test"]
    r = client.post(f"/profiles/{alice}/edit", data={"first_name": "Alice2"})
    assert r.status_code == 302


def test_kan_inte_andra_egen_roll(app, client):
    login(client, "alice_test")
    alice = app.test_ids["alice_test"]
    client.post(f"/profiles/{alice}/edit", data={"first_name": "Alice", "role": "admin"})
    with app.app_context():
        conn = get_db()
        role = conn.execute("SELECT role FROM users WHERE id = ?", (alice,)).fetchone()["role"]
        conn.close()
    assert role == "employee"


def test_ser_inte_andras_interna_anteckningar(app, client):
    login(client, "alice_test")
    bob = app.test_ids["bob_test"]
    r = client.get(f"/profiles/{bob}")
    assert r.status_code == 200
    assert b"Bob hemlig anteckning" not in r.data
