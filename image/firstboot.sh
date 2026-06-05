#!/usr/bin/env bash
set -euo pipefail

STAMP="/var/lib/weather-display/.firstboot_done"
LOG_DIR="/var/log/weather-display"
LOG_FILE="${LOG_DIR}/firstboot.log"

mkdir -p /var/lib/weather-display "${LOG_DIR}" /opt/weather-display/app/icons
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "[+] Weather display first boot starting"

if [ -f "${STAMP}" ]; then
    echo "[+] First boot already completed"
    exit 0
fi

export DEBIAN_FRONTEND=noninteractive

echo "[+] Installing default config"
if [ -f /boot/weather-display.env ]; then
    install -m 0600 /boot/weather-display.env /etc/default/weather-display
elif [ -f /boot/firmware/weather-display.env ]; then
    install -m 0600 /boot/firmware/weather-display.env /etc/default/weather-display
elif [ ! -f /etc/default/weather-display ]; then
    install -m 0600 /dev/null /etc/default/weather-display
    cat > /etc/default/weather-display <<'EOF'
WAVESHARE_DRIVER=V4
DISPLAY_ROTATE=0
DEVICE_HOSTNAME=weather-display
SSH_USER=weather
SSH_PASSWORD=weather
EOF
fi

set -a
. /etc/default/weather-display
set +a

configure_ssh_user() {
    local user_name="${SSH_USER:-weather}"
    local user_password="${SSH_PASSWORD:-weather}"
    local groups

    if ! printf '%s' "${user_name}" | grep -Eq '^[a-z_][a-z0-9_-]{0,31}$'; then
        echo "[!] Invalid SSH_USER '${user_name}'; skipping SSH user setup"
        return
    fi

    if [ -z "${user_password}" ]; then
        echo "[!] Empty SSH_PASSWORD; skipping SSH user setup"
        return
    fi

    groups="$(getent group sudo adm dialout video gpio i2c spi 2>/dev/null | cut -d: -f1 | paste -sd, -)"

    if id "${user_name}" >/dev/null 2>&1; then
        echo "[+] Updating SSH user ${user_name}"
    else
        echo "[+] Creating SSH user ${user_name}"
        if [ -n "${groups}" ]; then
            useradd -m -s /bin/bash -G "${groups}" "${user_name}"
        else
            useradd -m -s /bin/bash "${user_name}"
        fi
    fi

    printf '%s:%s\n' "${user_name}" "${user_password}" | chpasswd
    passwd -u "${user_name}" >/dev/null 2>&1 || true
    systemctl enable ssh || true
    systemctl restart ssh || true
}

configure_hostname() {
    local device_hostname="${DEVICE_HOSTNAME:-weather-display}"

    if [ -z "${device_hostname}" ]; then
        echo "[+] No DEVICE_HOSTNAME configured"
        return
    fi

    if ! printf '%s' "${device_hostname}" | grep -Eq '^[A-Za-z0-9][A-Za-z0-9-]{0,62}$'; then
        echo "[!] Invalid DEVICE_HOSTNAME '${device_hostname}'; skipping hostname setup"
        return
    fi

    echo "[+] Setting hostname to ${device_hostname}"
    printf '%s\n' "${device_hostname}" > /etc/hostname

    if grep -q '^127\.0\.1\.1' /etc/hosts; then
        sed -i "s/^127\.0\.1\.1.*/127.0.1.1\t${device_hostname}/" /etc/hosts
    else
        printf '127.0.1.1\t%s\n' "${device_hostname}" >> /etc/hosts
    fi

    hostnamectl set-hostname "${device_hostname}" || true
}

configure_wifi() {
    if [ -z "${WIFI_SSID:-}" ]; then
        echo "[+] No WIFI_SSID configured"
        return
    fi

    echo "[+] Configuring Wi-Fi"

    if [ -n "${WIFI_COUNTRY:-}" ] && command -v raspi-config >/dev/null 2>&1; then
        raspi-config nonint do_wifi_country "${WIFI_COUNTRY}" || true
    fi

    nmcli radio wifi on || true
    nmcli connection delete weather-display-wifi >/dev/null 2>&1 || true
    nmcli connection add \
        type wifi \
        ifname wlan0 \
        con-name weather-display-wifi \
        ssid "${WIFI_SSID}" || true

    nmcli connection modify weather-display-wifi connection.autoconnect yes || true

    if [ -n "${WIFI_PASSWORD:-}" ]; then
        nmcli connection modify weather-display-wifi \
            wifi-sec.key-mgmt wpa-psk \
            wifi-sec.psk "${WIFI_PASSWORD}" || true
    fi

    if [ "${WIFI_HIDDEN:-0}" = "1" ]; then
        nmcli connection modify weather-display-wifi wifi.hidden yes || true
    fi

    nmcli connection up weather-display-wifi || true
}

wait_for_network() {
    echo "[+] Waiting for network"
    if command -v nm-online >/dev/null 2>&1; then
        nm-online -q --timeout=45 || true
    fi

    for _ in $(seq 1 12); do
        if /usr/bin/python3 - <<'PY' >/dev/null 2>&1
from urllib.request import urlopen
urlopen("https://api.open-meteo.com", timeout=5).close()
PY
        then
            echo "[+] Network check passed"
            return
        fi
        sleep 5
    done

    echo "[!] Network check failed; weather update will retry on timer"
}

configure_ssh_user
configure_hostname
configure_wifi

echo "[+] Checking runtime packages"
if ! /usr/bin/python3 -c 'from PIL import Image; import spidev; import RPi.GPIO' >/dev/null 2>&1; then
    echo "[!] Runtime packages missing; rebuild the image with embedded dependencies"
fi
if [ ! -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf ] || [ ! -f /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf ]; then
    echo "[!] DejaVu fonts missing; install fonts-dejavu-core for correctly sized text"
fi

echo "[+] Checking Waveshare e-Paper library"
if command -v python3 >/dev/null 2>&1 && ! PYTHONPATH=/opt/weather-display/app /usr/bin/python3 -c 'from waveshare_epd import epd2in13_V4' >/dev/null 2>&1; then
    echo "[!] Waveshare driver missing; rebuild the image with the vendored waveshare_epd package"
fi

echo "[+] Running first boot display test"
if command -v python3 >/dev/null 2>&1; then
    /usr/bin/python3 /opt/weather-display/app/firstboot_test.py || true
fi

echo "[+] Generating icons"
if command -v python3 >/dev/null 2>&1; then
    /usr/bin/python3 /opt/weather-display/app/icons.py || true
fi

echo "[+] Enabling services"
systemctl enable location-lookup.service
systemctl enable --now weather-display.timer

echo "[+] Running boot location lookup"
systemctl start location-lookup.service || true

echo "[+] Running initial weather display update"
wait_for_network
systemctl start weather-display.service || true

touch "${STAMP}"
echo "[+] First boot complete"
