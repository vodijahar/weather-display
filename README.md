# Weather Display

Raspberry Pi Zero W / Zero 2 W weather display for Waveshare 2.13" e-paper.

## Features

- Raspberry Pi Zero W and Zero 2 W compatible
- Waveshare 2.13" e-paper V2/V3/V4 support
- Weather from Open-Meteo
- Location lookup runs on every boot
- Manual location works without IP geolocation
- Weather updates every 30 minutes
- Display only refreshes when weather changes
- No clock, to preserve e-ink lifespan

## Hardware

- Raspberry Pi Zero W or Zero 2 W
- Waveshare 2.13" e-paper display, V4 by default
- GPIO/SPI connection

## Build locally

This project builds a Raspberry Pi OS Lite 32-bit image for Pi Zero W / Zero 2 W. The output is a flashable image at `out/weather-display.img.xz`.

The image includes:

- the weather display app in `/opt/weather-display/app`
- the required Python runtime packages
- the vendored Waveshare Python display driver
- systemd units for first boot, location lookup, and weather refresh
- SPI enabled
- SSH enabled
- optional `image/weather-display.env`
- first-boot screen/Wi-Fi diagnostic

Install build tools:

```bash
sudo apt update
sudo apt install -y git rsync xz-utils util-linux e2fsprogs qemu-user-static binfmt-support
```

Download Raspberry Pi OS Lite 32-bit, then run:

```bash
./build-image.sh /path/to/raspios-lite.img.xz
```

You can also pass an already decompressed `.img` file:

```bash
./build-image.sh /path/to/raspios-lite.img
```

## Flash and Wi-Fi

Use Raspberry Pi Imager to flash `weather-display.img.xz`.

If Raspberry Pi Imager offers customisation settings before writing the SD card, configure:

- hostname
- username and password
- SSH
- Wi-Fi SSID and password
- Wi-Fi country

Current Raspberry Pi OS Lite uses NetworkManager, so do not use the old `wpa_supplicant.conf` boot-partition method for headless Wi-Fi setup.

If Imager does not offer Wi-Fi settings for the custom image, write the card first, then mount the boot partition before first boot and create `weather-display.env`:

```bash
WAVESHARE_DRIVER=V4
DISPLAY_ROTATE=0
DEVICE_HOSTNAME=weather-display
SSH_USER=weather
SSH_PASSWORD=weather

WIFI_SSID=YourNetworkName
WIFI_PASSWORD=YourNetworkPassword
WIFI_COUNTRY=ZA
WIFI_HIDDEN=0

WEATHER_LAT=-25.731340
WEATHER_LON=28.218370
WEATHER_CITY=Pretoria
```

The first-boot service reads this file, writes a NetworkManager profile, and then starts the normal setup flow. The boot partition is easy to read on another computer, so treat `weather-display.env` as sensitive if it contains a Wi-Fi password.

Default SSH login after first boot:

```bash
ssh weather@weather-display.local
```

Default password:

```text
weather
```

Change the password after logging in:

```bash
passwd
```

Change the hostname later:

```bash
sudo hostnamectl set-hostname new-hostname
sudo sed -i 's/^127\.0\.1\.1.*/127.0.1.1\tnew-hostname/' /etc/hosts
sudo reboot
```

### Changing Wi-Fi Later

After first boot, edit the saved NetworkManager connection over SSH:

```bash
nmcli connection show
sudo nmcli connection modify weather-display-wifi wifi.ssid "NewNetworkName"
sudo nmcli connection modify weather-display-wifi wifi-sec.psk "NewNetworkPassword"
sudo nmcli connection down weather-display-wifi
sudo nmcli connection up weather-display-wifi
```

For a hidden network:

```bash
sudo nmcli connection modify weather-display-wifi wifi.hidden yes
```

To change Wi-Fi country:

```bash
sudo raspi-config nonint do_wifi_country ZA
```

If the Pi is moved somewhere you cannot SSH into it, mount the boot partition on another computer, add a fresh `weather-display.env`, then reset first boot from the Pi before rebooting:

```bash
sudo rm /var/lib/weather-display/.firstboot_done
sudo reboot
```

### Optional config

Create `image/weather-display.env` before building to override defaults copied to the boot partition:

```bash
cp image/weather-display.env.example image/weather-display.env
```

The default display driver is `WAVESHARE_DRIVER=V4`.

If you provide `WEATHER_LAT` and `WEATHER_LON`, the device skips IP geolocation and can complete first boot without Wi-Fi. Live weather still requires network access; if weather fetch fails, the screen shows a waiting-for-Wi-Fi status instead of failing silently.

The image must include the Waveshare Python driver at `/opt/weather-display/app/waveshare_epd`. First boot does not download executable driver code.
