# Latest Huawei Router Force 4G & CLI Tool

A lightweight Python command-line tool to force **4G/LTE Only** mode and interact with modern Huawei Mobile Wi-Fi and LTE routers from your terminal.

Older shell scripts fail with `Couldn't log in` on newer Huawei firmware because modern models use **SCRAM-SHA256 (`password_type` 4)** authentication. This tool uses `huawei-lte-api` with explicit session login to work reliably on newer Huawei routers.

## Features
- **Force Network Bands:** Lock to `4g` only, `3g` only, or revert to `auto`.
- **Signal & Device Status:** Inspect exact 4G metrics (`RSRP`, `RSRQ`, `SINR`, `RSSI`), battery percentage, and connected devices.
- **Data Usage Stats:** Check current session and monthly download/upload totals.
- **SMS Management:** Read inbox messages and send SMS directly from the terminal.
- **Remote Reboot:** Restart your router with a single command.

## Requirements
- Python 3.8+
- `huawei-lte-api`

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com
   cd huawei-4g-cli
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

```bash
# Force 4G/LTE only
./huawei_cli.py 4g

# Revert to Auto (4G/3G/2G)
./huawei_cli.py auto

# Force 3G only
./huawei_cli.py 3g

# Check 4G signal quality (RSRP/SINR), battery, and connected users
./huawei_cli.py status

# View session and monthly data usage
./huawei_cli.py stats

# Read the 5 most recent SMS messages
./huawei_cli.py sms

# Send an SMS
./huawei_cli.py send +251911223344 "Hello from terminal"

# Reboot the router
./huawei_cli.py reboot
```

## Troubleshooting
- **`100003: No rights (needs login)` or Login Errors:** Huawei Mobile Wi-Fi routers usually allow only **one active admin session** at a time. Make sure you are logged out of the web dashboard (`http://192.168.8.1`) in your browser before running commands.
- **Connection Timeout:** Verify that you are connected to your router's Wi-Fi or USB network and that `ROUTER_IP` matches your gateway IP.

## License
MIT License