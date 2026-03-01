import urllib.request
import urllib.error
import json
import time
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
CACHE_FILE = os.path.join(BASE_DIR, 'last_ip.txt')
LOG_FILE = os.path.join(BASE_DIR, 'ddns_updater.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        logging.error("Configuration file not found. Please create config.json.")
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_public_ip():
    try:
        req = urllib.request.Request(
            'https://api.ipify.org',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8').strip()
    except Exception as e:
        logging.error(f"Failed to get public IP: {e}")
        return None

def get_last_ip():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_ip(ip):
    with open(CACHE_FILE, 'w') as f:
        f.write(ip)

def update_ddns(record, ip):
    url = f"https://dynamicdns.park-your-domain.com/update?host={record['host']}&domain={record['domain']}&password={record['password']}&ip={ip}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            logging.info(f"DDNS update response for {record['host']}.{record['domain']}: {result}")
            return True
    except Exception as e:
        logging.error(f"Failed to update DDNS for {record['host']}.{record['domain']}: {e}")
        return False

def check_and_update(force=False):
    config = load_config()
    if not config:
        return

    current_ip = get_public_ip()
    if not current_ip:
        return

    last_ip = get_last_ip()

    if force or current_ip != last_ip:
        if force:
            logging.info(f"Initial run or force update requested. Updating DDNS records with current IP {current_ip}...")
        else:
            logging.info(f"IP changed from {last_ip} to {current_ip}. Updating DDNS records...")
        records = config.get('records', [])
        if not records:
            logging.warning("No records found in configuration.")
            return

        all_success = True
        for record in records:
            if not update_ddns(record, current_ip):
                all_success = False

        if all_success:
            save_last_ip(current_ip)
            logging.info("All DDNS records updated successfully.")
        else:
            logging.error("One or more DDNS updates failed. IP cache not updated, will retry next time.")
    else:
        logging.info(f"IP remains {current_ip}. No update needed.")

def main():
    logging.info("Starting DDNS Updater Service...")
    
    # Force update on startup
    try:
        check_and_update(force=True)
    except Exception as e:
        logging.error(f"Unexpected error during initial force update: {e}")

    while True:
        try:
            config = load_config()
            interval = config.get('check_interval_seconds', 300) if config else 300
            
            time.sleep(interval)
            check_and_update()
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            time.sleep(300)

if __name__ == '__main__':
    main()
