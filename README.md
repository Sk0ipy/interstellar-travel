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
| 3 | Wachtwoordhergebruik (flightops) | A07:2021 – Identification and Authentication Failures | SSH op de target-VM |
| 4 | Misconfigured sudoers | A05:2021 – Security Misconfiguration | target-VM, account `flightops` |
| 5 | Verouderde/open interne service | A06:2021 – Vulnerable and Outdated Components | target-VM, poort 8080 (nergens gelinkt) |
| 6 | Onbeveiligde file-upload (reverse shell) | A08:2021 – Software and Data Integrity Failures | target-VM, uploadpagina op poort 8080 |
| extra | Overmatige data-exposure in de API | A01:2021 – Broken Access Control | `/api/destinations` (geeft ook `beacon_signal` terug) |

Kwetsbaarheden 1 en 2 zitten in deze repo (website + Flask-backend). Kwetsbaarheden 3 t/m 6
staan als setup-script in `vm-setup/server/` en draaien op dezelfde Ubuntu-VM als de website
(één target-VM; een tweede VM is je eigen aanvaller-machine). Zie `vm-setup/README.md`.

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
Dat wachtwoord is op de target-VM hergebruikt voor SSH (kwetsbaarheid 3) en is de ingang naar
root-toegang via de sudoers-fout (kwetsbaarheid 4) en uiteindelijk het controlepaneel
(kwetsbaarheden 5 en 6) — alles op diezelfde VM, zie `vm-setup/`.

### Kwetsbaarheden 3–6

6. **SSH met het gelekte wachtwoord.** `ssh flightops@<target-ip>` met het wachtwoord uit
   stap hiervoor.
7. **Sudoers-fout (kwetsbaarheid 4).** `sudo -l` laat zien dat `flightops` `sudo python3` mag
   draaien zonder wachtwoord — klassieke GTFOBins-escalatie:
   `sudo python3 -c 'import os; os.system("/bin/bash")'`. Dat geeft root en **vlag**
   `VS{ROOT_ON_LAUNCH_SERVER}` in `/root/flag_root.txt`.
8. **Ongelinkte, open service (kwetsbaarheid 5).** Een portscan (`nmap <target-ip>`) vindt
   poort 8080: een dashboard zonder enige login, nergens vanaf de website gelinkt, met
   **vlag** `VS{INTERNAL_PANEL_FOUND}` erop.
9. **Onbeveiligde upload → reverse shell (kwetsbaarheid 6).** De uploadknop op dat dashboard
   accepteert elk bestand ongevalideerd; een taak voert elk ge-uploade `.py`-bestand elke minuut
   als root uit. Upload een script met een reverse-shell-payload, vang hem op met een listener
   op je aanvaller-VM, en lees `/root/flag_shell.txt`: **vlag** `VS{CONTROL_PANEL_SHELL}`.

## Dwaalspoor

`/crew` (link "Crew login" in de header): zwak standaardwachtwoord (Welkom + oprichtingsjaar), maar binnen staat alleen een alleen-lezen archief van oude boekingen. Geen vlag, geen route verder.
