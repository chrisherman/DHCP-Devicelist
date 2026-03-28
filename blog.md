# I Built a Dashboard Just So I Never Have to Use My Router’s Terrible Web UI Again

If you manage a home lab, a small office network, or just suffer from an uncontrollable urge to buy random smart home gadgets, you’ve definitely played the worst game in IT: *"Where the hell did that IP address go?"*

You plug in a new Raspberry Pi, a smart plug, or a network-attached storage drive. The lights blink. It's alive. And then... nothing. You have no idea what IP address the DHCP server just handed it. 

So, you reluctantly navigate to your router's web interface. You know the one—it looks like it was designed in 2004, takes 15 seconds to load a basic HTML table, and aggressively logs you out the exact microsecond you look away from the screen. After clicking through six menus, you finally find the DHCP lease list. Half the devices are named something incredibly helpful like `espressif_A1B2C3`, `android-78234y89234`, or my personal favorite: `Unknown Device`. 

Ah yes, *Unknown Device*. That really narrows it down.

I decided I value my sanity too much to keep doing this. So, I built a way to bypass my router's tragic UI entirely.

Enter **[DHCP-Devicelist](https://github.com/chrisherman/DHCP-Devicelist)**.

## The Solution: A Dashboard for Humans

`DHCP-Devicelist` is a lightweight, Dockerized web application born out of pure frustration. It connects directly to your routers, rips the active DHCP leases out of them, and presents them in a clean, searchable web dashboard that actually loads in this century.

Instead of fighting with a clunky admin portal, you get a simple, unified page showing:
*   **IP Address**
*   **MAC Address**
*   **Friendly Device Name** (e.g., "Living Room Apple TV" instead of a random string of hexadecimal nonsense).

It lets you dynamically add or remove multiple routers right from the UI, triggers manual scans the second you plug in new hardware, and refreshes automatically in the background.

## How It Works (Without the Suffering)

To keep the application fast and stop it from breaking every time a router vendor pushes a bad firmware update, I built it with a few heavily automated components:

### 1. SNMP Polling (Because Screen-Scraping is for Masochists)
Instead of trying to screen-scrape a proprietary web UI designed by someone who clearly hates humanity, the backend relies on the ancient but reliable **Simple Network Management Protocol (SNMP)**. 

A Python script uses `snmpwalk` to politely ask the routers for their ARP and DHCP tables. It grabs the active IP addresses and maps them to their hardware MAC addresses before the router can complain.

### 2. Device Name Translation (Fixing Vendor Stupidity)
A MAC address isn't very helpful unless you are a machine. The app uses a `known_devices.json` file as a local database to map MAC addresses to names you actually recognize. Whenever the script fetches a lease table, it intercepts the MAC addresses and translates them. 

Now, instead of seeing `b8:27:eb:xx:xx:xx`, the dashboard proudly displays `Pi-Hole DNS Server`. Magic.

### 3. A Web UI That Doesn't Hate You
The extracted data is saved locally, and a lightweight Python Flask server serves up the frontend interface. 

The frontend uses modern JavaScript to display a clean, sortable table. Because the data is loaded asynchronously, you can sort by IP, MAC, or Name instantly—no page reloads required. If you launch the app for the first time, a dialog box prompts you to add a router. You can manage which routers are being actively polled via simple checkboxes, or delete them entirely, directly from your browser. 

### 4. Background Scheduling and the "I Need It Now" Button
The application runs on a continuous daily schedule. But let’s be real, if you just spun up a new virtual machine or plugged in a new sensor, you don't want to wait 24 hours. A prominent "Sync Now" button triggers an immediate SNMP poll, refreshing the dashboard in seconds.

### 5. Dockerized (Because Dependency Hell is Real)
Nobody wants to install SNMP tools, Python, and a dozen random libraries directly onto their host operating system. The entire application is packaged into a single Docker container. 

A simple `docker-compose up -d` handles the environment, ports, and volume mapping for persistent storage. It's truly plug-and-play, leaving your host OS blissfully untouched.

## Try It Out

If you're tired of logging into your router just to find out where your smart toaster went, or you just want a better bird's-eye view of your LAN without the headache, you can spin this up in a few seconds. 

The project is fully open-source, probably has fewer bugs than your router's firmware, and is available right now:  
👉 **[DHCP-Devicelist on GitHub](https://github.com/chrisherman/DHCP-Devicelist)**

It includes a comprehensive `README` with instructions on how to map your known devices, enable SNMP, and deploy the container.

Take back control of your network, and may you never have to guess what `Unknown Device` is ever again.