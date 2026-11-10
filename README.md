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

## Kwetsbaarheden

| # | Kwetsbaarheid | OWASP / categorie | Waar op de planeet |
|---|---|---|---|
| 1 | SQL-injectie in de admin-login | A03:2021 – Injection | `/admin` (POST, website/backend) |
| 2 | Local File Inclusion in de downloadfunctie | A01:2021 – Broken Access Control (path traversal) | `/api/bookings/manifest?file=` |
| 3 | Wachtwoordhergebruik (flightops) | A07:2021 – Identification and Authentication Failures | SSH op de lanceerserver-VM |
| 4 | Misconfigured sudoers | A05:2021 – Security Misconfiguration | lanceerserver-VM, account `flightops` |
| 5 | Verouderde/open interne service | A06:2021 – Vulnerable and Outdated Components | controlepaneel-VM (alleen vanaf de lanceerserver bereikbaar) |
| 6 | Onbeveiligde file-upload (reverse shell) | A08:2021 – Software and Data Integrity Failures | controlepaneel-VM, uploadpagina |
| extra | Overmatige data-exposure in de API | A01:2021 – Broken Access Control | `/api/destinations` (geeft ook `beacon_signal` terug) |

Kwetsbaarheden 1 en 2 zitten in deze repo (website + Flask-backend) en zijn hieronder getest.
Kwetsbaarheden 3 t/m 6 horen op de Ubuntu-VM's (lanceerserver + controlepaneel) die de crew los opzet;
die zijn hier nog niet gebouwd.

## Winnend pad

1. **Ontdekken van /admin.** Drie manieren: `robots.txt` (Disallow: /admin), scannen met gobuster, of de planeet draaien en 3x op het verborgen kristal klikken (achterzijde, nabij de zuidpool).
2. **Inloggen op /admin — twee routes:**
   - **Bedoelde route:** de crewfoto op "Over ons" heet `<gebruikersnaam>_<wachtwoord>.svg` (zie de `img src` in de broncode).
   - **Kwetsbaarheid 1 (SQLi):** de login bouwt de query met stringopbouw. Gebruikersnaam `' OR '1'='1' -- ` en een willekeurig wachtwoord logt in zonder de echte gegevens te kennen.
   - Beide routes geven **vlag 2** (`FLAG_ADMIN`) op `/admin/panel`.
3. **Database vinden.** Het systeemlogboek in het adminpaneel noemt `/admin/database` en zegt dat de toegangscode het beacon-signaal van Kepra Relay is.
4. **Verstopte vlag = toegangscode.** `GET /api/destinations` geeft bij Kepra Relay het veld `beacon_signal` terug: **vlag 1** (`FLAG_HIDDEN`).
5. **Lanceerdata.** Met die code opent /admin/database; de rij IT-999 bevat **vlag 3** (`FLAG_LAUNCH`).

### Kwetsbaarheid 2 (LFI) — brug naar de VM's

Na het boeken van een vlucht (`/boeken`) staat er een downloadknop voor het boekingsbestand
(`/api/bookings/manifest?file=<referentie>.txt`). De bestandsnaam uit de queryparameter wordt
zonder validatie gebruikt, dus `?file=../private/ops_notes.txt` ontsnapt uit de boekingsmap.
Dat bestand bevat **vlag extra** (`FLAG_LFI`) en het wachtwoord van het account `flightops`.
Dat wachtwoord is op de lanceerserver-VM hergebruikt voor SSH (kwetsbaarheid 3) en is de ingang
naar de root-toegang via de sudoers-fout (kwetsbaarheid 4) en uiteindelijk het controlepaneel
(kwetsbaarheden 5 en 6).

## Dwaalspoor

`/crew` (link "Crew login" in de header): zwak standaardwachtwoord (Welkom + oprichtingsjaar), maar binnen staat alleen een alleen-lezen archief van oude boekingen. Geen vlag, geen route verder.
