#!/usr/bin/env bash
# VM1 "lanceerserver": zet kwetsbaarheid 3 (wachtwoordhergebruik via SSH) en
# kwetsbaarheid 4 (misconfigured sudoers) neer. Draai als root: sudo ./setup.sh
set -euo pipefail

OPS_USER="flightops"
OPS_PASSWORD="F1ightOps!2026"          # moet gelijk zijn aan backend/config.py: OPS_PASSWORD
CONTROLEPANEEL_IP="192.168.56.20"      # pas aan naar het interne IP van VM2
CONTROLEPANEEL_PORT="8080"
FLAG_ROOT="VS{ROOT_ON_LAUNCH_SERVER}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Draai dit script met sudo." >&2
  exit 1
fi

# --- kwetsbaarheid 3: account met hergebruikt wachtwoord, SSH-login op wachtwoord ---
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
cat > /etc/sudoers.d/90-flightops <<EOF
${OPS_USER} ALL=(ALL) NOPASSWD: /usr/bin/python3
EOF
chmod 440 /etc/sudoers.d/90-flightops
visudo -c -f /etc/sudoers.d/90-flightops

# --- vlag + doorverwijzing naar het controlepaneel, alleen leesbaar als root ---
cat > /root/flag_root.txt <<EOF
Root bereikt op lanceerserver via de misconfigured sudoers-regel voor flightops:

    sudo python3 -c 'import os; os.system("/bin/bash")'

VLAG: ${FLAG_ROOT}

Interne systemen: controlepaneel draait op ${CONTROLEPANEEL_IP}:${CONTROLEPANEEL_PORT}
(alleen bereikbaar vanaf dit netwerk, niet vanaf buiten).
EOF
chmod 600 /root/flag_root.txt

echo "Klaar. flightops kan nu via SSH inloggen en 'sudo python3' draaien zonder wachtwoord."
echo "Root-vlag staat in /root/flag_root.txt."
