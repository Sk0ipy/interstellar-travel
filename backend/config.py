"""Instellingen voor de Interstellar Travel-machine.

Alles in dit bestand zijn spelwaarden voor de TryHackMe-room (geen echte geheimen).
Pas ze hier aan; de rest van de code leest ze vanuit dit bestand.
"""

# Admin-account. De inloggegevens zitten in de bestandsnaam van de crewfoto op
# de pagina "Over ons": <gebruikersnaam>_<wachtwoord>.svg
ADMIN_USER = "fleetadmin"
ADMIN_PASSWORD = "Orbit-Kepra-2026"
ADMIN_IMAGE_NAME = f"{ADMIN_USER}_{ADMIN_PASSWORD}.svg"

# Dwaalspoor: crew-login met een zwak standaardwachtwoord, zonder nuttige data.
CREW_USER = "crew"
CREW_PASSWORD = "Welkom2024"

# Kwetsbaarheid 3 (op de Ubuntu-VM): account dat via SSH met dit wachtwoord
# inlogt. Het wachtwoord lekt via kwetsbaarheid 2 (LFI) in het boekingsbestand.
OPS_USER = "flightops"
OPS_PASSWORD = "F1ightOps!2026"

# Vlaggen
FLAG_HIDDEN = "VS{BEACON_SIGNAL_FOUND}"       # verstopt in de API van de bestemmingen; opent de database
FLAG_ADMIN = "VS{ADMIN_PANEL_ACCESS}"         # staat in het adminpaneel na het inloggen (ook via SQLi te krijgen)
FLAG_LAUNCH = "VS{LAUNCH_DATA_RETRIEVED}"     # staat in de lanceerdata in de database
FLAG_LFI = "VS{LFI_BOOKING_MANIFEST}"         # staat in het interne bestand buiten de boekingsmap (LFI)

SECRET_KEY = "interstellar-travel-dev-key-change-me"
