# DHCP-Devicelist: A Centralized Dashboard for LAN Devices

## Why
Locating the IP addresses of devices on a local network can be tedious. It usually requires logging into router web interfaces to view DHCP lease tables, where devices are often listed with unhelpful manufacturer default names or simply as "Unknown". 

## What
[DHCP-Devicelist](https://github.com/chrisherman/DHCP-Devicelist) is a lightweight, Dockerized web application. It connects to your network routers, extracts active DHCP leases, and displays them in a clean, searchable, and sortable web dashboard. The application translates raw MAC addresses into human-readable friendly names.

## How
The application relies on several core components to automate this process:

*   **SNMP Polling:** A background Python script uses `snmpwalk` to query the configured routers for their ARP and DHCP tables. This maps active IP addresses to their hardware MAC addresses.
*   **Device Name Translation:** A local `known_devices.json` file maps MAC addresses to user-defined friendly names. 
*   **Web Dashboard:** A Python Flask server hosts a frontend interface. The UI allows users to sort devices, dynamically add or remove routers to be monitored, and view the network state.
*   **Scheduling:** Data refreshes automatically every 24 hours. A "Sync Now" button triggers an immediate on-demand SNMP poll for newly connected devices.
*   **Deployment:** The entire application is packaged into a single Docker container, deployable via `docker-compose` with persistent volumes for user configuration.

Source code and installation instructions are available on GitHub: [DHCP-Devicelist](https://github.com/chrisherman/DHCP-Devicelist).
