# VM-opzet voor kwetsbaarheden 3–6

Je gebruikt twee VM's:

| VM | Rol |
|---|---|
| **Target** | draait de website, de Flask-backend en alles voor kwetsbaarheden 1 t/m 6 |
| **Aanvaller** | jouw eigen pentest-VM (bijv. Kali/Parrot) waarmee je het target aanvalt |

Alleen de **target**-VM heeft een setup-script nodig — dat staat in `vm-setup/server/`.
De aanvaller-VM hoeft niets van deze repo te hebben; die gebruik je gewoon om `nmap`,
`gobuster`, `ssh`, een reverse-shell-listener (`nc -lvnp <poort>`), etc. te draaien.

## 1. Target-VM opzetten

Ubuntu Server 22.04 LTS, netwerk zo dat je er met SSH/HTTP bij kan vanaf je aanvaller-VM
(bijv. beide op "Intern netwerk" of "Host-only" in VirtualBox, of allebei NAT met
portforwarding).

Op de target-VM:

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/Sk0ipy/interstellar-travel.git
cd interstellar-travel
sudo ./vm-setup/server/setup.sh
```

Dit script:
- builat en draait de website + Flask-backend op **poort 5000** (kwetsbaarheden 1–2),
- maakt het account `flightops` aan met SSH-login op wachtwoord (kwetsbaarheid 3),
- zet een te brede sudoers-regel voor `flightops` neer (kwetsbaarheid 4),
- start een ongelinkt, niet-geauthenticeerd controlepaneel op **poort 8080** (kwetsbaarheid 5),
- laat een taak elke minuut elk ge-uploade `.py`-bestand daar als root uitvoeren
  (kwetsbaarheid 6).

Het script is idempotent: opnieuw draaien overschrijft alleen zijn eigen configuratie.

## 2. Hoe het één keten vormt

1. Speler vindt via `robots.txt` / gobuster / de verborgen hotspot `/admin`.
2. **Kwetsbaarheid 1 (SQLi)** of de bedoelde route via "Over ons" → ingelogd als admin.
3. Databasepaneel → **kwetsbaarheid 1-vervolg**: verstopte vlag via `/api/destinations`
   (`beacon_signal`) als toegangscode → lanceerdata-vlag.
4. Speler boekt een vlucht en downloadt het boekingsbestand → **kwetsbaarheid 2 (LFI)**:
   `?file=../private/ops_notes.txt` lekt het wachtwoord van `flightops`.
5. **Kwetsbaarheid 3:** `ssh flightops@<target-ip>` met dat wachtwoord.
6. **Kwetsbaarheid 4:** `sudo -l` toont `sudo python3` zonder wachtwoord →
   `sudo python3 -c 'import os; os.system("/bin/bash")'` → root, vlag in `/root/flag_root.txt`.
7. **Kwetsbaarheid 5:** een portscan (`nmap <target-ip>`) vindt poort 8080 — een dashboard
   zonder login, nergens vanaf de website gelinkt.
8. **Kwetsbaarheid 6:** upload een `.py`-bestand met een reverse-shell-payload via dat
   dashboard, vang de verbinding op met `nc -lvnp <poort>` op je aanvaller-VM, en lees
   `/root/flag_shell.txt`.

Zie `server/setup.sh` voor de exacte wachtwoorden en vlaggen.
