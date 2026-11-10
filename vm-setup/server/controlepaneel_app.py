"""Controlepaneel: dashboard-app voor kwetsbaarheden 5 en 6.

Kwetsbaarheid 5: dit dashboard heeft geen enkele authenticatie en staat nergens
gelinkt vanaf de publieke website — alleen te vinden door de poort (8080) te
scannen, bijvoorbeeld met nmap.

Kwetsbaarheid 6: de uploadpagina accepteert elk bestand zonder enige validatie
(geen extensie-check, geen contentcheck). Een cronjob (zie setup.sh) voert elk
.py-bestand in de uploadmap uit als root, dus een uploadend script met een
reverse shell krijgt direct een root-shell op deze machine.
"""
from pathlib import Path

from flask import Flask, abort, redirect, request, url_for

UPLOAD_DIR = Path("/opt/panel/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

FLAG_PANEL = "VS{INTERNAL_PANEL_FOUND}"

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><title>Controlepaneel</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 40px auto;">
  <h1>Interstellar Travel — Controlepaneel</h1>
  <p>Beheerdashboard voor lanceeroperaties. Niet publiek gelinkt, geen login vereist.</p>
  <p><strong>Statusvlag:</strong> {flag}</p>
  <h2>Bestanden</h2>
  <ul>{files}</ul>
  <h2>Upload (onderhoudsscripts)</h2>
  <form method="post" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <button type="submit">Uploaden</button>
  </form>
  <p>Ge-uploade bestanden worden elke minuut automatisch door de onderhoudstaak verwerkt.</p>
</body></html>
"""


@app.get("/")
def dashboard():
    files = "".join(f"<li>{f.name}</li>" for f in sorted(UPLOAD_DIR.iterdir())) or "<li>(leeg)</li>"
    return PAGE.format(flag=FLAG_PANEL, files=files)


@app.post("/upload")
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        abort(400)
    # Kwetsbaarheid 6: geen enkele validatie van naam, extensie of inhoud.
    f.save(UPLOAD_DIR / f.filename)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
