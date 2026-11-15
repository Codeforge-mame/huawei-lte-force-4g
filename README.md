
A lightweight Python command-line tool to force **4G/LTE Only** mode, lock LTE frequency bands, toggle mobile data, switch Wi-Fi bands, and interact with modern Huawei Mobile Wi-Fi and LTE routers from your terminal.

Older shell scripts fail with `Couldn't log in` on newer Huawei firmware because modern models use **SCRAM-SHA256 (`password_type` 4)** authentication. This tool uses `huawei-lte-api` with explicit session login to work reliably on newer Huawei routers.

## Features
- **Force Network Mode:** Lock to `4g` only, `3g` only, or revert to `auto`.
- **LTE Band Locking:** Lock specific cellular frequencies (`b1`, `b3`, `b5`, `b7`, `b8`, `b20`, `b28`, `b38`, `b40`, `b41`, or `all`) to avoid congested towers.
- **Mobile Data Control:** Turn cellular mobile data `on` or `off` instantly without turning off Wi-Fi.
- **Wi-Fi Frequency Switching:** Toggle local Wi-Fi between `2.4g` (longer range) and `5g` (faster speeds) on dual-band models.
- **Signal & Device Status:** Inspect exact 4G metrics (`RSRP`, `RSRQ`, `SINR`, `RSSI`), active Wi-Fi band, battery percentage, and connected devices (`devices`).
- **Data Usage Stats:** Check current session and monthly download/upload totals.
- **SMS Management:** Read inbox messages and send SMS directly from the terminal.
- **Remote Reboot:** Restart your router with a single command.

## Requirements
- Python 3.8+
- `huawei-lte-api`

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/Codeforge-mame/huawei-lte-force-4g
   cd huawei-lte-force-4g
   ```

2. **Install the required library:**
   ```bash
   pip install huawei-lte-api
   ```
   *(On newer Ubuntu/Debian systems, use `pip install --user --break-system-packages huawei-lte-api` or a virtual environment.)*

3. **Configure your router credentials:**
   Copy the example config file and add your router's IP and admin/Wi-Fi password:
   ```bash
   cp .env.example .env
   chmod 600 .env
   nano .env
   ```
   *(Alternatively, save your config at `~/.huawei_router_env` so you can run the script from any directory.)*

## Usage

### Network & Radio Control
```bash
# Force 4G/LTE only
./huawei_cli.py 4g

# Revert to Auto (4G/3G/2G)
./huawei_cli.py auto

# Force 3G only
./huawei_cli.py 3g

# Lock a specific 4G LTE frequency band (e.g., Band 3 / 1800MHz or Band 20 / 800MHz)
./huawei_cli.py band b3
./huawei_cli.py band all

# Enable or disable mobile data
./huawei_cli.py data off
./huawei_cli.py data on

# Switch Wi-Fi frequency band between 2.4GHz and 5GHz (dual-band routers only)
./huawei_cli.py wifi 5g
./huawei_cli.py wifi 2.4g
```

### Monitoring, Devices & SMS
```bash
# Check 4G signal quality (RSRP/SINR), Wi-Fi band, battery, and connected users
./huawei_cli.py status

# List connected Wi-Fi devices (Hostname, IP, MAC)
./huawei_cli.py devices

# View session and monthly data usage
./huawei_cli.py stats

# Read the 5 most recent SMS messages
./huawei_cli.py sms

# Send an SMS
./huawei_cli.py send +251911223344 "Hello from terminal"

# Reboot the router
./huawei_cli.py reboot
```

## Test Status
- Tested on a **Huawei 4G Pocket Router** and confirmed working. If you encounter any errors or compatibility issues on your model, feel free to open an Issue or reach out.

## Troubleshooting
- **`100003: No rights (needs login)` or Login Errors:** Huawei Mobile Wi-Fi routers usually allow only **one active admin session** at a time. Make sure you are logged out of the web dashboard (`http://192.168.8.1`) in your browser before running commands.
- **Hardware Support:** Switching to `wifi 5g` or locking specific LTE bands requires hardware support on your router model. If your pocket router is 2.4GHz-only or does not support a specific band, stick to `wifi 2.4g` and `band all`.
- **Connection Timeout:** Verify that you are connected to your router's Wi-Fi or USB network and that `ROUTER_IP` matches your gateway IP.

## License
MIT License
