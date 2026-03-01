# NamecheapAutoDDNS

A lightweight, zero-dependency Python script for Windows that automatically updates Namecheap Dynamic DNS (DDNS) records when your public IP address changes.

**Supported Operating Systems:**
- Windows 10 (32-bit & 64-bit)
- Windows 11 (64-bit)

It runs completely in the background as a Windows Scheduled Task, and requires nothing more than a simple configuration file.

## Features

- **Zero Dependencies**: Uses only standard Python libraries (`urllib`, `json`, etc.).
- **Portable python Environment**: The `setup.cmd` script automatically downloads an isolated, embeddable release of Python 3.14.3. It won't conflict with your existing system Python.
- **Background Service**: Automatically registers itself in the Windows Task Scheduler to run silently on startup.
- **Multi-Record Support**: Update multiple subdomains or domains at once in a single configuration file.
- **Smart Update**: Caches your last known IP locally and only pings the Namecheap API when an actual IP change is detected.
- **Concise & Rotating Logs**: Automatically parses Namecheap's XML responses for clean, human-readable log messages. Creates daily log files and retains only the last 5 days to save disk space.

## Setup Instructions

1. **Configure your Domains**:
   Rename or copy the `config.json.example` file to `config.json`, then open it and fill it with your Namecheap DDNS information.
   *Note: To get your dynamic DNS password, log into Namecheap, select your domain, go to Advanced DNS, and scroll down to the Dynamic DNS section.*

   ```json
   {
       "check_interval_seconds": 300,
       "records": [
           {
               "host": "@",
               "domain": "example.com",
               "password": "your_dynamic_dns_password_here"
           },
           {
               "host": "www",
               "domain": "example.com",
               "password": "your_dynamic_dns_password_here"
           }
       ]
   }
   ```
   * `check_interval_seconds`: How often the script checks your public IP (default is 300 seconds / 5 minutes).
   * `host`: The subdomain you are updating (e.g., `@` for root, `www`, `subdomain`).
   * `domain`: Your main domain name.
   * `password`: The Dynamic DNS Password from your Namecheap dashboard.

2. **Install and Run**:
   - Right-click on `setup.cmd` and select **"Run as administrator"**.
   - The script will download the Python environment, configure the scheduled task, and immediately start the background service.

## Stopping and Uninstalling

If you want to stop the service and remove it from your system startup:
- Right-click on `uninstall.cmd` and select **"Run as administrator"**.
- This will stop any currently running python instances of the updater and unregister the Windows Scheduled Task.

## Troubleshooting

- **Check the logs**: The script writes its operation status, including IP changes and parsed API responses, to date-stamped log files (e.g., `logs/ddns_updater_YYYY-MM-DD.log`) located in the new `logs` subdirectory.
- **Scheduled Task Issues**: Open "Task Scheduler" in Windows and look for `AutoDDNS_Updater` to manually start, stop, or check the last run status of the script.
