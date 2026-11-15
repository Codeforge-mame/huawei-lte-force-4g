#!/usr/bin/env python3
import sys
from pathlib import Path
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from huawei_lte_api.enums.net import NetworkModeEnum
from huawei_lte_api.enums.sms import BoxTypeEnum

# Common LTE Band Bitmasks (Hexadecimal)
LTE_BANDS = {
    "all": "7FFFFFFFFFFFFFFF",
    "b1": "1",             # 2100 MHz
    "b3": "4",             # 1800 MHz
    "b5": "10",            # 850 MHz
    "b7": "40",            # 2600 MHz
    "b8": "80",            # 900 MHz
    "b20": "80000",        # 800 MHz
    "b28": "8000000",      # 700 MHz
    "b38": "2000000000",   # 2600 MHz TDD
    "b40": "8000000000",   # 2300 MHz TDD
    "b41": "10000000000",  # 2500 MHz TDD
}

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

Network & Band Commands:
  4g                    Force 4G/LTE only mode
  3g                    Force 3G only mode
  auto                  Set network mode to Auto (4G/3G/2G)
  band <preset|hex>     Lock LTE frequency band (all, b1, b3, b7, b8, b20, b28, b38, b40, b41)
  data <on|off>         Enable or disable mobile data connection
  wifi <2.4g|5g>        Switch Wi-Fi frequency band (2.4GHz or 5GHz)

Monitoring & Device Commands:
  status                Show signal strength (RSRP/SINR), battery, and network type
  stats                 Show current session & monthly data usage
  devices               List connected Wi-Fi devices (Name, IP, MAC)
  sms                   Read recent inbox SMS messages
  send <num> <msg>      Send an SMS message
  reboot                Reboot the router
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

            elif cmd == "band":
                if len(sys.argv) < 3:
                    print("Usage: ./huawei_cli.py band <all|b1|b3|b7|b8|b20|b28|b38|b40|b41|hex>")
                    sys.exit(1)
                preset = sys.argv[2].lower()
                lte_hex = LTE_BANDS.get(preset, preset)
                current = client.net.net_mode()
                client.net.set_net_mode(lte_hex, current["NetworkBand"], current["NetworkMode"])
                print(f"Success: LTE band set to {preset.upper()} (0x{lte_hex})")

            elif cmd == "data":
                if len(sys.argv) < 3 or sys.argv[2].lower() not in ("on", "off"):
                    print("Usage: ./huawei_cli.py data <on|off>")
                    sys.exit(1)
                state = 1 if sys.argv[2].lower() == "on" else 0
                client.dial_up.set_mobile_dataswitch(state)
                print(f"Success: Mobile data turned {'ON' if state == 1 else 'OFF'}")

            elif cmd == "wifi":
                if len(sys.argv) < 3 or sys.argv[2].lower() not in ("2.4g", "5g"):
                    print("Usage: ./huawei_cli.py wifi <2.4g|5g>")
                    sys.exit(1)
                choice = sys.argv[2].lower()
                freq_val = "1" if choice == "5g" else "0"
                # Fetch current basic settings to preserve SSID/security while updating frequency
                basic = client.wlan.basic_settings()
                if isinstance(basic, list):
                    basic = basic[0]
                basic["WifiFrequency"] = freq_val
                client.wlan.set_basic_settings(basic)
                print(f"Success: Wi-Fi frequency switched to {choice.upper()} (Wi-Fi may reconnect briefly)")

            elif cmd == "devices":
                hosts = client.wlan.host_list()
                host_list = hosts.get("Hosts", {}).get("Host", [])
                if isinstance(host_list, dict):
                    host_list = [host_list]
                if not host_list:
                    print("No connected devices found.")
                for h in host_list:
                    print(f"- {h.get('HostName', 'Unknown')} | IP: {h.get('IpAddress')} | MAC: {h.get('MacAddress')}")

            elif cmd == "status":
                status = client.monitoring.status()
                signal = client.device.signal()
                freq = "5GHz" if str(status.get("wififrequence")) == "1" else "2.4GHz"
                print(f"Network Type : {status.get('CurrentNetworkType')} (19 = 4G/LTE)")
                print(f"Signal Bars  : {status.get('SignalIcon')}/{status.get('maxsignal')}")
                print(f"RSRP / RSRQ  : {signal.get('rsrp')} / {signal.get('rsrq')}")
                print(f"SINR / RSSI  : {signal.get('sinr')} / {signal.get('rssi')}")
                print(f"Wi-Fi Band   : {freq}")
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
        print("Tip: Close any open router web dashboard tabs (192.168.8.1) or check if your hardware supports this setting.")

if __name__ == "__main__":
    main()
