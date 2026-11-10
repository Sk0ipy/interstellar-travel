#!/usr/bin/env bash
# De ENE target-VM: website + Flask-backend (kwetsbaarheden 1-2, al in de repo),
# plus kwetsbaarheden 3 (wachtwoordhergebruik SSH), 4 (misconfigured sudoers),
# 5 (onbeveiligd/ongelinkt intern dashboard) en 6 (onbeveiligde upload -> reverse shell).
#
# Draai dit vanuit de hoofdmap van de gekloonde repo op de target-VM:
#   git clone https://github.com/Sk0ipy/interstellar-travel.git
#   cd interstellar-travel
#   sudo ./vm-setup/server/setup.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OPS_USER="flightops"
OPS_PASSWORD="F1ightOps!2026"          # moet gelijk zijn aan backend/config.py: OPS_PASSWORD
FLAG_ROOT="VS{ROOT_ON_LAUNCH_SERVER}"
FLAG_SHELL="VS{CONTROL_PANEL_SHELL}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Draai dit script met sudo." >&2
  exit 1
fi

echo "==> Pakketten installeren"
apt-get update -y
apt-get install -y python3 python3-venv python3-pip python3-flask nodejs npm

echo "==> Website builden"
cd "${REPO_DIR}/website"
npm install
npm run build

echo "==> Backend-service (website + vuln 1-2) op poort 5000"
VENV="${REPO_DIR}/backend/.venv"
python3 -m venv "${VENV}"
"${VENV}/bin/pip" install flask

cat > /etc/systemd/system/interstellar-backend.service <<EOF
[Unit]
Description=Interstellar Travel - website + backend
After=network.target

[Service]
WorkingDirectory=${REPO_DIR}/backend
ExecStart=${VENV}/bin/python3 ${REPO_DIR}/backend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# --- kwetsbaarheid 3: account met hergebruikt wachtwoord, SSH-login op wachtwoord ---
echo "==> flightops-account + SSH"
if ! id "$OPS_USER" &>/dev/null; then
  useradd -m -s /bin/bash "$OPS_USER"
fi
echo "${OPS_USER}:${OPS_PASSWORD}" | chpasswd

sed -i \
  -e 's/^#\?PasswordAuthentication .*/PasswordAuthentication yes/' \
  -e 's/^#\?PermitRootLogin .*/PermitRootLogin no/' \
  /etc/ssh/sshd_config
systemctl restart ssh

# --- kwetsbaarheid 4: misconfigured sudoers ---
# Ops-team heeft dit ooit toegevoegd om een deploy-script te kunnen draaien, maar liet het
# te breed staan: elke sudo python3-aanroep werkt zonder wachtwoord, en python3 kan alles.
echo "==> Misconfigured sudoers"
cat > /etc/sudoers.d/90-flightops <<EOF
${OPS_USER} ALL=(ALL) NOPASSWD: /usr/bin/python3
EOF
chmod 440 /etc/sudoers.d/90-flightops
visudo -c -f /etc/sudoers.d/90-flightops

cat > /root/flag_root.txt <<EOF
Root bereikt via de misconfigured sudoers-regel voor flightops:

    sudo python3 -c 'import os; os.system("/bin/bash")'

VLAG: ${FLAG_ROOT}

Zoek verder op deze machine naar interne diensten op andere poorten.
EOF
chmod 600 /root/flag_root.txt

# --- kwetsbaarheid 5 + 6: controlepaneel op poort 8080, upload -> root via cron ---
echo "==> Controlepaneel (vuln 5-6) op poort 8080"
mkdir -p /opt/panel/uploads
cp "${REPO_DIR}/vm-setup/server/controlepaneel_app.py" /opt/panel/app.py

if ! id panel &>/dev/null; then
  useradd -r -s /usr/sbin/nologin -d /opt/panel panel
fi
chown -R panel:panel /opt/panel

cat > /etc/systemd/system/controlepaneel.service <<'EOF'
[Unit]
Description=Interstellar Travel controlepaneel
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

cat > /opt/panel/run_maintenance.sh <<'EOF'
#!/usr/bin/env bash
for f in /opt/panel/uploads/*.py; do
  [ -e "$f" ] || continue
  timeout 10 python3 "$f" || true
done
EOF
chmod +x /opt/panel/run_maintenance.sh

( crontab -l 2>/dev/null | grep -v run_maintenance.sh ; \
  echo "* * * * * /opt/panel/run_maintenance.sh" ) | crontab -

cat > /root/flag_shell.txt <<EOF
Als dit bestand via een reverse shell is gelezen: gefeliciteerd, je hebt een
.py-bestand geüpload naar het controlepaneel en de taak die elke minuut draait
heeft het als root uitgevoerd.

VLAG: ${FLAG_SHELL}
EOF
chmod 600 /root/flag_shell.txt

systemctl daemon-reload
systemctl enable --now interstellar-backend.service
systemctl enable --now controlepaneel.service

echo ""
echo "Klaar."
echo "  - Website:        http://<vm-ip>:5000"
echo "  - Controlepaneel: http://<vm-ip>:8080 (niet gelinkt, alleen te vinden via portscan)"
echo "  - SSH:            flightops@<vm-ip>  (wachtwoord lekt via de LFI-kwetsbaarheid)"
