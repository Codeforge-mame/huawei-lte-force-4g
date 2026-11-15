#!/usr/bin/env python3
import sys
from pathlib import Path
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from huawei_lte_api.enums.net import NetworkModeEnum
from huawei_lte_api.enums.sms import BoxTypeEnum

# Load credentials from local .env or ~/.huawei_router_env
def load_config():
    config = {
        "ROUTER_IP": "192.168.8.1",
        "ROUTER_USER": "admin",
        "ROUTER_PASS": "",
    }
    for env_path in [Path(".env"), Path.home() / ".huawei_router_env"]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip('"').strip("'")
            break
    return config

def print_help():
    print("""Huawei Modern Router CLI (Supports SCRAM / Password Type 4)

Usage: ./huawei_cli.py <command> [arguments]

Commands:
  4g                  Force 4G/LTE only mode
  3g                  Force 3G only mode
  auto                Set network mode to Auto (4G/3G/2G)
  status              Show signal strength (RSRP/SINR), battery, and network type
  stats               Show current session & monthly data usage
  sms                 Read recent inbox SMS messages
  send <num> <msg>    Send an SMS message
  reboot              Reboot the router
""")

def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if float(size) < 1024.0:
            return f"{float(size):.2f} {unit}"
        size = float(size) / 1024.0
    return f"{size:.2f} PB"

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    cfg = load_config()
    if not cfg["ROUTER_PASS"]:
        print("Error: ROUTER_PASS is not set. Create a .env file (see README.md).")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    url = f"http://{cfg['ROUTER_IP']}/"

    try:
        with Connection(url, username=cfg["ROUTER_USER"], password=cfg["ROUTER_PASS"]) as connection:
            client = Client(connection)
            client.user.login()

            if cmd in ("4g", "3g", "auto"):
                modes = {
                    "4g": NetworkModeEnum.MODE_4G_ONLY,
                    "3g": NetworkModeEnum.MODE_3G_ONLY,
                    "auto": NetworkModeEnum.MODE_AUTO,
                }
                current = client.net.net_mode()
                client.net.set_net_mode(current["LTEBand"], current["NetworkBand"], modes[cmd])
                print(f"Success: Network mode set to {cmd.upper()}")

            elif cmd == "status":
                status = client.monitoring.status()
                signal = client.device.signal()
                print(f"Network Type : {status.get('CurrentNetworkType')} (19 = 4G/LTE)")
                print(f"Signal Bars  : {status.get('SignalIcon')}/{status.get('maxsignal')}")
                print(f"RSRP / RSRQ  : {signal.get('rsrp')} / {signal.get('rsrq')}")
                print(f"SINR / RSSI  : {signal.get('sinr')} / {signal.get('rssi')}")
                print(f"Battery      : {status.get('BatteryPercent')}%")
                print(f"Connected    : {status.get('CurrentWifiUser')} device(s)")

            elif cmd == "stats":
                traffic = client.monitoring.traffic_statistics()
                month = client.monitoring.month_statistics()
                print(f"Session Down : {format_bytes(traffic.get('CurrentDownload', 0))}")
                print(f"Session Up   : {format_bytes(traffic.get('CurrentUpload', 0))}")
                print(f"Month Down   : {format_bytes(month.get('CurrentMonthDownload', 0))}")
                print(f"Month Up     : {format_bytes(month.get('CurrentMonthUpload', 0))}")

            elif cmd == "sms":
                messages = client.sms.get_sms_list(box_type=BoxTypeEnum.LOCAL_INBOX, read_count=5)
                sms_list = messages.get("Messages", {}).get("Message", [])
                if isinstance(sms_list, dict):
                    sms_list = [sms_list]
                if not sms_list:
                    print("Inbox is empty.")
                for m in sms_list:
                    print(f"[{m.get('Date')}] From {m.get('Phone')}: {m.get('Content')}")

            elif cmd == "send":
                if len(sys.argv) < 4:
                    print("Usage: ./huawei_cli.py send <phone_number> <message>")
                    sys.exit(1)
                phone = sys.argv[2]
                text = " ".join(sys.argv[3:])
                client.sms.send_sms([phone], text)
                print(f"SMS sent to {phone}")

            elif cmd == "reboot":
                client.device.reboot()
                print("Router is rebooting...")

            else:
                print(f"Unknown command: {cmd}")
                print_help()

    except Exception as e:
        print(f"Error: {e}")
        print("Tip: Close any open router web dashboard tabs (192.168.8.1) and try again.")

if __name__ == "__main__":
    main()
