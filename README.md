# DHCP Extractor

This project provides a Dockerized application that creates a simple web server to display devices and IP addresses issued by your router's DHCP server. It pulls data from your router via SNMP and provides a clean, sortable web interface showing online/offline status, IP, MAC address, and hostname.

<img width="2504" height="796" alt="image" src="https://github.com/user-attachments/assets/f6eb3355-0dc4-4652-ba82-c363ed78e3d7" />

## Features
- **Multiple Router Support:** Dynamically add, edit, and toggle multiple routers directly from the web interface.
- **Device Tracking:** Displays all active/known DHCP leases from your routers.
- **Online Status:** Pings devices to verify if they are currently online.
- **Device Identification:** Automatically resolves DNS hostnames, uses an OUI vendor database to identify unknown devices, or allows manual mapping.
- **Manual Refresh:** Trigger a scan directly from the web interface to update the device list in real-time.

## Requirements
- A router that supports **SNMP v2c**.
- **SNMP must be enabled** on your routers.
- Docker and Docker Compose installed on your host machine.

## Installation

1. **Clone the Repository**
   Pull the project from GitHub:
   ```bash
   git clone https://github.com/your-username/dhcpfetch2.git
   cd dhcpfetch2
   ```

2. **Install Docker**
   Ensure you have Docker and Docker Compose installed on your host machine. 
   If you don't have Docker installed, you can find the official installation guidance here:
   - [Get Docker](https://docs.docker.com/get-docker/)
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

3. **Build and Run the Container**
   Create and start the Docker container in the background:
   ```bash
   docker compose up -d --build
   ```
   *(Note: Use `docker-compose` if you are using an older version of Docker Compose).*

   This will build the image, start the container (named `er605-extractor`), and run it in the background using the host's network.

## Configuration

1. **Adding Routers:**
   When you first start the application and access the web interface, you'll be prompted to add your router's Friendly Name, IP address, and SNMP Community string. You can add as many routers as you need. The configuration is saved persistently in `routers.json`.

2. **Customizing Device Names:**
   You can manually map MAC addresses to readable names by editing `known_devices.json` in the project root. 
   Format the MAC addresses in lowercase and separate bytes with colons (`:`).
   Example:
   ```json
   {
       "00:11:22:33:44:55": "My Custom Device",
       "aa:bb:cc:dd:ee:ff": "Living Room TV"
   }
   ```

## Accessing the Web Interface

Once the container is running, open your web browser and navigate to the IP address of the machine hosting the Docker container. By default, it runs on port 80:

```
http://<your-docker-host-ip>/
```

From the interface, you can sort devices by clicking on the table headers, or click "Scan Now" to force an immediate refresh of the DHCP table.

## Troubleshooting
- **No devices showing up:** Ensure your router IP and SNMP Community strings are correct in the router configuration, and that your router has SNMP enabled.
- **Scan Now button failing:** Check the container logs using `docker logs er605-extractor` for any errors.