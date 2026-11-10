# VM-opzet voor kwetsbaarheden 3–6

Deze map bevat de scripts voor de twee Ubuntu-VM's die kwetsbaarheden 3 t/m 6 hosten.
De website + Flask-backend (kwetsbaarheden 1–2) staan los hiervan in `website/` en `backend/`.

```
vm-setup/
  lanceerserver/     VM1: SSH-login met hergebruikt wachtwoord (3) + misconfigured sudoers (4)
  controlepaneel/    VM2: open interne service (5) + onbeveiligde upload -> reverse shell (6)
```

## 1. VM's aanmaken (VirtualBox)

Maak **twee** Ubuntu Server 22.04 LTS VM's aan:

| VM | Naam | Netwerk |
|---|---|---|
| VM1 | `lanceerserver` | Adapter 1: NAT (voor SSH vanaf je laptop) · Adapter 2: Intern netwerk `vs-internal` |
| VM2 | `controlepaneel` | Adapter 1: Intern netwerk `vs-internal` (géén NAT — alleen bereikbaar vanaf VM1) |

Zet bij beide VM's 2 CPU's / 2GB RAM / 20GB disk. Installeer Ubuntu Server met een gewoon
gebruikersaccount (niet "flightops" — dat account maakt het setup-script zelf aan).

Geef VM2 een vast intern IP, bijvoorbeeld `192.168.56.20`, en noteer het IP van VM1 op
hetzelfde interne netwerk (bijvoorbeeld `192.168.56.10`). Beide scripts vragen hier niet om —
pas zelf de variabelen boven in `setup.sh` aan als je andere IP's gebruikt.

## 2. Scripts draaien

Kopieer elke map naar de bijbehorende VM (bijv. met `scp -r vm-setup/lanceerserver gebruiker@<ip>:~`)
en draai op elke VM:

```bash
cd lanceerserver   # of controlepaneel
chmod +x setup.sh
sudo ./setup.sh
```

De scripts zijn idempotent: opnieuw draaien overschrijft alleen de eigen configuratie.

## 3. Hoe het samen een keten vormt

1. **Kwetsbaarheid 2 (LFI, al gebouwd)** lekt het wachtwoord van `flightops`.
2. **Kwetsbaarheid 3 — wachtwoordhergebruik:** dat wachtwoord werkt via SSH op `lanceerserver` (VM1).
3. **Kwetsbaarheid 4 — misconfigured sudoers:** `flightops` mag `sudo python3` draaien zonder
   wachtwoord. Dat opent een root-shell → `/root/flag_root.txt`. Daar staat ook het interne
   IP/poort van `controlepaneel`.
4. **Kwetsbaarheid 5 — open interne service:** vanaf `lanceerserver` is `controlepaneel:8080`
   bereikbaar: een dashboard zonder enige authenticatie → `FLAG_PANEL`.
5. **Kwetsbaarheid 6 — onbeveiligde upload:** de uploadpagina op dat dashboard accepteert elk
   bestand zonder validatie. Een nachtelijke taak draait elk ge-uploade `.py`-bestand als root —
   dat geeft een reverse shell → `/root/flag_shell.txt` op `controlepaneel`.

Zie `lanceerserver/setup.sh` en `controlepaneel/setup.sh` voor de exacte vlaggen en wachtwoorden.
