import os
import json
import subprocess
import socket
import time
import threading
import datetime
from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# Config
ROUTER_IP = os.getenv('ROUTER_IP', '192.168.2.1')
COMMUNITY = os.getenv('SNMP_COMMUNITY', 'test')
OUTPUT_FILE = '/var/www/html/dhcp_table.json'
MAPPING_FILE = 'known_devices.json'
ROUTERS_FILE = '/app/data/routers.json'
is_scanning = False


def load_routers():
    if os.path.exists(ROUTERS_FILE):
        try:
            with open(ROUTERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_routers(routers):
    os.makedirs(os.path.dirname(ROUTERS_FILE), exist_ok=True)
    with open(ROUTERS_FILE, 'w') as f:
        json.dump(routers, f, indent=4)

def get_manufacturer(mac):
    """
    Identifies the vendor using the first 6 digits (OUI).
    Data sourced from IEEE public registries.
    """
    prefixes = {
        # IoT & Home Automation
        "dc:56:7b": "Espressif (IoT)", "e8:16:56": "Tuya Smart", 
        "08:f9:e0": "Tuya/Tasmota", "cc:50:e3": "Hyleton/Hi-Link",
        "5c:cf:7f": "Espressif (ESP8266)", "dc:da:0c": "Espressif (ESP32)",
        "00:04:20": "Logitech (Harmony)", "f0:f6:c1": "Sonos",
        # Mobile & Computers
        "98:01:a7": "Apple Inc.", "90:cd:e8": "Apple (iPhone)",
        "3c:61:05": "Valve (Steam Deck)", "2e:c4:d3": "Locally Administered",
        # Networking & Infrastructure
        "24:f5:a2": "Linksys", "20:23:51": "TP-Link (Archer)",
        "00:1c:2b": "Hive Hub", "52:54:00": "QEMU/KVM Virtual",
        # Smart Assistants
        "20:fe:00": "Amazon Technologies", "44:00:49": "Amazon Echo",
        "ec:8a:c4": "Amazon (Kindle/Fire)"
    }
    # Match the first three bytes (e.g., '5a:18:ba')
    prefix = mac[:8].lower()
    return prefixes.get(prefix, "Unknown Manufacturer")

def get_hostname(ip):
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except: return "Unknown"

def is_online(ip):
    cmd = ["ping", "-c", "1", "-W", "1", ip]
    return subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0

def run_extraction():
    global is_scanning
    if is_scanning: return
    is_scanning = True
    
    try:
        known_map = {}
        if os.path.exists(MAPPING_FILE):
            try:
                with open(MAPPING_FILE, 'r') as f:
                    raw_map = json.load(f)
                    known_map = {k.strip().lower().replace("-", ":"): v for k, v in raw_map.items()}
            except: pass

        existing_devices = {}
        if os.path.exists(OUTPUT_FILE):
            try:
                with open(OUTPUT_FILE, 'r') as f:
                    old_data = json.load(f)
                    existing_devices = {d['mac']: d for d in old_data.get('devices', [])}
            except: pass

        table = []
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        routers = load_routers()
        
        for router in routers:
            if not router.get("enabled", True):
                continue
                
            router_ip = router.get("ip")
            community = router.get("community", COMMUNITY)
            
            # Perfect pairing logic using OID index
            mac_oid = ".1.3.6.1.2.1.4.22.1.2"
            mac_lines = get_snmp_data(mac_oid, router_ip, community)

            for line in mac_lines:
                try:
                    if "Hex-STRING:" not in line: continue
                    parts = line.split(" = ")
                    ip = ".".join(parts[0].split('.')[-4:])
                    raw_mac = parts[1].replace("Hex-STRING: ", "").strip().lower()
                    clean_mac = raw_mac.replace(" ", ":").replace("-", ":")
                    
                    # 1. Check Manual Mapping
                    display_name = known_map.get(clean_mac)
                    
                    # 2. Check DNS Hostname
                    if not display_name:
                        dns_name = get_hostname(ip)
                        if dns_name != "Unknown":
                            display_name = dns_name
                        else:
                            # 3. Fallback to Manufacturer Identification
                            display_name = get_manufacturer(clean_mac)

                    online_status = is_online(ip)
                    last_seen = current_time if online_status else existing_devices.get(clean_mac, {}).get('last_seen', 'Never')

                    table.append({
                        "hostname": display_name,
                        "ip": ip,
                        "mac": clean_mac,
                        "online": online_status,
                        "last_seen": last_seen,
                        "router": router.get("name", "Unknown")
                    })
                except: continue

        with open(OUTPUT_FILE, 'w') as f:
            json.dump({"last_updated": current_time, "devices": table}, f, indent=4)
    finally:
        is_scanning = False

def get_snmp_data(oid, router_ip, community):
    try:
        cmd = ["snmpwalk", "-v2c", "-c", community, router_ip, oid]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        return result.strip().split('\n')
    except: return []


@app.route('/routers', methods=['GET'])
def get_routers():
    return jsonify(load_routers())

@app.route('/routers', methods=['POST'])
def add_router():
    data = request.json
    routers = load_routers()
    new_router = {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "ip": data.get("ip"),
        "community": data.get("community", COMMUNITY),
        "enabled": data.get("enabled", True)
    }
    routers.append(new_router)
    save_routers(routers)
    return jsonify({"status": "success", "router": new_router})

@app.route('/routers/<router_id>', methods=['PUT', 'PATCH'])
def update_router(router_id):
    data = request.json
    routers = load_routers()
    for r in routers:
        if r.get("id") == router_id:
            if "enabled" in data: r["enabled"] = data["enabled"]
            if "name" in data: r["name"] = data["name"]
            if "ip" in data: r["ip"] = data["ip"]
            if "community" in data: r["community"] = data["community"]
            break
    save_routers(routers)
    return jsonify({"status": "success"})

@app.route('/routers/<router_id>', methods=['DELETE'])
def delete_router(router_id):
    routers = load_routers()
    routers = [r for r in routers if r.get("id") != router_id]
    save_routers(routers)
    return jsonify({"status": "success"})

@app.route('/refresh')
def refresh():
    threading.Thread(target=run_extraction).start()
    return jsonify({"status": "started"})

def run_schedule():
    while True:
        time.sleep(86400)
        run_extraction()

if __name__ == "__main__":
    threading.Thread(target=run_schedule, daemon=True).start()
    threading.Thread(target=run_extraction).start()
    app.run(host='0.0.0.0', port=5000)
