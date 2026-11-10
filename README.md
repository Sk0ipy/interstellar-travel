# Interstellar Travel

Reisbureau voor raketreizen tussen planeten, gebouwd als kwetsbare machine voor een TryHackMe-room.

```
VanguardSpace/
  website/   React + three.js: de draaibare planeet en alle publieke pagina's
  backend/   Flask + SQLite: API, /admin, database, robots.txt
  *.blend    Blender-model van de planeet (planet.glb in website/public)
```

## Starten

Ontwikkelen (twee terminals):

```
cd backend
.venv\Scripts\python.exe -m flask --app app run --port 5000

cd website
npm run dev          # http://localhost:5173 (proxy naar Flask voor /api, /admin, /static)
```

Productie-achtig (alleen Flask, serveert de gebouwde site op poort 5000):

```
cd website && npm run build
cd ../backend && .venv\Scripts\python.exe app.py
```

Alle spelwaarden (inloggegevens, vlaggen) staan in `backend/config.py`.

## Winnend pad

1. **Ontdekken van /admin.** Drie manieren: `robots.txt` (Disallow: /admin), scannen met gobuster, of de planeet draaien en 3x op het verborgen kristal klikken (achterzijde, nabij de zuidpool).
2. **Inloggegevens.** De crewfoto op "Over ons" heet `<gebruikersnaam>_<wachtwoord>.svg` (zie de `img src` in de broncode). Inloggen op /admin geeft **vlag 2** (`FLAG_ADMIN`).
3. **Database vinden.** Het systeemlogboek in het adminpaneel noemt `/admin/database` en zegt dat de toegangscode het beacon-signaal van Kepra Relay is.
4. **Verstopte vlag = toegangscode.** `GET /api/destinations` geeft bij Kepra Relay het veld `beacon_signal` terug: **vlag 1** (`FLAG_HIDDEN`).
5. **Lanceerdata.** Met die code opent /admin/database; de rij IT-999 bevat **vlag 3** (`FLAG_LAUNCH`).

## Dwaalspoor

`/crew` (link "Crew login" in de header): zwak standaardwachtwoord (Welkom + oprichtingsjaar), maar binnen staat alleen een alleen-lezen archief van oude boekingen. Geen vlag, geen route verder.

## Nog te doen (kwetsbaarheden)

De huidige machine heeft bewust slechte praktijken (informatielek in de API, inloggegevens in een bestandsnaam,
zwak standaardwachtwoord, hint in robots.txt) maar nog geen volledige lijst van minimaal zes OWASP-kwetsbaarheden.
Kies die als crew en voeg ze toe voordat het ontwerp wordt ingeleverd.
