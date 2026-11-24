"""Interstellar Travel: Flask-backend voor de TryHackMe-room.

Routes
  /                      React-site (dist), met SPA-fallback
  /api/...               JSON voor vluchten, bestemmingen, boekingen, crew-login (dwaalspoor)
  /admin                 inlogpagina voor administrators
  /admin/panel           adminpaneel (vlag 2)
  /admin/database        database met toegangscode (vlag 1 opent hem, vlag 3 is het einddoel)
  /robots.txt            hint naar /admin
"""
import hmac
import secrets
from functools import wraps
from pathlib import Path

from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request, send_from_directory, session, url_for)

import config
import db

BASE = Path(__file__).parent
DIST = BASE.parent / "website" / "dist"

app = Flask(__name__, static_folder=str(BASE / "static"), static_url_path="/static")
app.secret_key = config.SECRET_KEY
db.init_db()


def install_team_image():
    """Zet de crewfoto neer onder een bestandsnaam met de admin-inloggegevens."""
    target_dir = BASE / "static" / "team"
    target_dir.mkdir(parents=True, exist_ok=True)
    for old in target_dir.glob("*.svg"):
        old.unlink()
    (target_dir / config.ADMIN_IMAGE_NAME).write_bytes((BASE / "assets" / "team_photo.svg").read_bytes())


def install_private_notes():
    """Zet het interne notitiebestand neer dat buiten de boekingsmap staat
    (het doelwit van de LFI-kwetsbaarheid, kwetsbaarheid 2)."""
    target_dir = BASE / "private"
    target_dir.mkdir(exist_ok=True)
    (target_dir / "ops_notes.txt").write_text(
        "INTERSTELLAR TRAVEL - INTERNE NOTITIE (ground-ops)\n"
        "Niet voor openbare toegang.\n\n"
        "Service-account voor het check-in-systeem (SSH op de lanceerserver):\n"
        f"  gebruiker: {config.OPS_USER}\n"
        f"  wachtwoord: {config.OPS_PASSWORD}\n\n"
        "Opmerking: dit wachtwoord staat ook op het gedeelde groundops-account.\n"
        "Niet hergebruiken op andere systemen.\n\n"
        f"VLAG: {config.FLAG_LFI}\n",
        encoding="utf-8",
    )


install_team_image()
install_private_notes()


def rows(query, args=()):
    conn = db.connect()
    try:
        return [dict(r) for r in conn.execute(query, args).fetchall()]
    finally:
        conn.close()


def same(a, b):
    return hmac.compare_digest(a.encode(), b.encode())


# ---------------------------------------------------------------- publieke API

@app.get("/api/flights")
def api_flights():
    return jsonify(rows("SELECT code, destination, departs, duration, price, seats, kind, bookable "
                        "FROM flights ORDER BY id"))


@app.get("/api/destinations")
def api_destinations():
    # Let op: dit endpoint geeft alle kolommen terug, ook beacon_signal (verstopte vlag).
    return jsonify(rows("SELECT * FROM destinations ORDER BY id"))


@app.get("/api/about")
def api_about():
    return jsonify(team_image=f"/static/team/{config.ADMIN_IMAGE_NAME}")


MANIFEST_DIR = BASE / "bookings"
PRIVATE_DIR = BASE / "private"


def write_manifest(reference, name, email, code):
    """Zet het boekingsbestand neer dat de speler straks via de downloadlink ophaalt."""
    MANIFEST_DIR.mkdir(exist_ok=True)
    (MANIFEST_DIR / f"{reference}.txt").write_text(
        "INTERSTELLAR TRAVEL - BOEKINGSBESTAND\n"
        f"Referentie: {reference}\n"
        f"Naam: {name}\n"
        f"E-mail: {email}\n"
        f"Vlucht: {code}\n\n"
        "# interne configuratie (niet verwijderen, gebruikt door check-in-systeem)\n"
        "checkin_service=ground-ops-v3\n"
        "sync_endpoint=internal://ground-ops\n",
        encoding="utf-8",
    )


@app.post("/api/book")
def api_book():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    code = str(data.get("flight", "")).strip()
    if not name or "@" not in email or not code:
        return jsonify(error="Vul naam, e-mailadres en vlucht in."), 400
    flight = rows("SELECT * FROM flights WHERE code = ?", (code,))
    if not flight:
        return jsonify(error="Onbekende vlucht."), 404
    if not flight[0]["bookable"]:
        return jsonify(error="Deze vlucht is gesloten vracht en kan niet geboekt worden."), 403
    if flight[0]["seats"] <= 0:
        return jsonify(error="Deze vlucht is vol."), 409
    reference = "IT-" + secrets.token_hex(3).upper()
    conn = db.connect()
    conn.execute("INSERT INTO bookings (reference, name, email, flight_code) VALUES (?,?,?,?)",
                 (reference, name, email, code))
    conn.execute("UPDATE flights SET seats = seats - 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    write_manifest(reference, name, email, code)
    return jsonify(reference=reference, flight=code)


@app.get("/api/bookings/manifest")
def api_manifest():
    """Kwetsbaarheid 2: de bestandsnaam uit de queryparameter wordt zonder
    validatie aan de map geplakt, waardoor path traversal (LFI) mogelijk is."""
    name = request.args.get("file", "")
    target = MANIFEST_DIR / name
    if not target.is_file():
        abort(404)
    return Response(target.read_text(encoding="utf-8", errors="replace"), mimetype="text/plain")


# ------------------------------------------------------ dwaalspoor: crew-login

@app.post("/api/crew-login")
def api_crew_login():
    data = request.get_json(silent=True) or {}
    if (same(str(data.get("username", "")), config.CREW_USER)
            and same(str(data.get("password", "")), config.CREW_PASSWORD)):
        session["crew"] = True
        return jsonify(ok=True)
    return jsonify(error="Onjuiste gebruikersnaam of wachtwoord."), 401


@app.get("/api/crew/bookings")
def api_crew_bookings():
    if not session.get("crew"):
        return jsonify(error="Niet ingelogd."), 401
    return jsonify(rows("SELECT reference, passenger, flight_code, status FROM old_bookings ORDER BY id"))


# ---------------------------------------------------------------- admin

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapper


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """Kwetsbaarheid 1: de login bouwt de SQL-query met stringopbouw, waardoor
    gebruikersinvoer rechtstreeks in de query terechtkomt (SQL-injectie)."""
    error = None
    if request.method == "POST":
        user = request.form.get("username", "")
        password = request.form.get("password", "")
        query = (
            "SELECT * FROM administrators WHERE username = '" + user + "'"
            " AND password = '" + password + "'"
        )
        conn = db.connect()
        try:
            row = conn.execute(query).fetchone()
        except Exception:
            row = None
        finally:
            conn.close()
        if row is not None:
            session["admin"] = True
            session["admin_user"] = row["username"]
            return redirect(url_for("admin_panel"))
        error = "Onjuiste gebruikersnaam of wachtwoord."
    return render_template("admin_login.html", error=error), (401 if error else 200)


@app.get("/admin/panel")
@admin_required
def admin_panel():
    return render_template("admin_panel.html", flag=config.FLAG_ADMIN)


@app.route("/admin/database", methods=["GET", "POST"])
@admin_required
def admin_database():
    error = None
    if request.method == "POST":
        if same(request.form.get("code", "").strip(), config.FLAG_HIDDEN):
            session["db"] = True
        else:
            error = "Toegangscode ongeldig."
    if not session.get("db"):
        return render_template("admin_gate.html", error=error)
    return render_template(
        "admin_database.html",
        launches=rows("SELECT * FROM launches ORDER BY id"),
        bookings=rows("SELECT reference, name, flight_code, created FROM bookings ORDER BY id DESC LIMIT 20"),
    )


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# ---------------------------------------------------------------- overig

@app.get("/robots.txt")
def robots():
    text = ("User-agent: *\n"
            "Disallow: /admin\n"
            "Disallow: /api/crew/\n")
    return Response(text, mimetype="text/plain")


@app.get("/<path:path>")
@app.get("/")
def spa(path=""):
    """Serveer de gebouwde React-site; onbekende paden vallen terug op index.html."""
    if path.startswith(("api/", "admin", "static/")):
        abort(404)
    target = DIST / path
    if path and target.is_file():
        return send_from_directory(DIST, path)
    if (DIST / "index.html").is_file():
        return send_from_directory(DIST, "index.html")
    return "Bouw de site eerst met 'npm run build' in de map website.", 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
