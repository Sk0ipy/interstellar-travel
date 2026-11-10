#!/usr/bin/env bash
# VM2 "controlepaneel": zet kwetsbaarheid 5 (open interne service) en
# kwetsbaarheid 6 (onbeveiligde upload -> reverse shell als root) neer.
# Draai als root: sudo ./setup.sh   (app.py moet in dezelfde map staan)
set -euo pipefail

INTERNAL_SUBNET="192.168.56.0/24"      # pas aan naar jouw interne netwerk
FLAG_SHELL="VS{CONTROL_PANEL_SHELL}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Draai dit script met sudo." >&2
  exit 1
fi

apt-get update -y
apt-get install -y python3 python3-pip python3-flask ufw

mkdir -p /opt/panel/uploads
cp "${SCRIPT_DIR}/app.py" /opt/panel/app.py

# --- service draait als eigen laagrechten-gebruiker ---
if ! id panel &>/dev/null; then
  useradd -r -s /usr/sbin/nologin -d /opt/panel panel
fi
chown -R panel:panel /opt/panel

cat > /etc/systemd/system/controlepaneel.service <<'EOF'
[Unit]
Description=Interstellar Travel controlepaneel (intern dashboard)
After=network.target

[Service]
User=panel
Group=panel
WorkingDirectory=/opt/panel
ExecStart=/usr/bin/python3 /opt/panel/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now controlepaneel.service

# --- alleen bereikbaar vanaf het interne netwerk, niet van buiten (kwetsbaarheid 5
#     is het ontbreken van authenticatie op de app zelf, niet een open poort naar het
#     publieke internet) ---
ufw allow from "${INTERNAL_SUBNET}" to any port 8080 proto tcp
ufw --force enable

# --- kwetsbaarheid 6: nachtelijke "onderhoudstaak" voert elk ge-uploade .py-bestand
#     uit als root. Dit is de integriteitsfout: niemand controleert wat daar binnenkomt. ---
cat > /opt/panel/run_maintenance.sh <<EOF
#!/usr/bin/env bash
for f in /opt/panel/uploads/*.py; do
  [ -e "\$f" ] || continue
  timeout 10 python3 "\$f" || true
done
EOF
chmod +x /opt/panel/run_maintenance.sh

( crontab -l 2>/dev/null | grep -v run_maintenance.sh ; \
  echo "* * * * * /opt/panel/run_maintenance.sh" ) | crontab -

cat > /root/flag_shell.txt <<EOF
Als dit bestand via een reverse shell is gelezen: gefeliciteerd, je hebt een
.py-bestand geüpload naar het controlepaneel en de nachtelijke (eigenlijk: elke
minuut draaiende) onderhoudstaak heeft het als root uitgevoerd.

VLAG: ${FLAG_SHELL}
EOF
chmod 600 /root/flag_shell.txt

echo "Klaar. Controlepaneel draait op poort 8080, alleen bereikbaar vanaf ${INTERNAL_SUBNET}."
echo "Shell-vlag staat in /root/flag_shell.txt (root-only)."
