import urllib.request
import urllib.error
import json
import time
import logging
import os
import xml.etree.ElementTree as ET

import datetime
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
CACHE_FILE = os.path.join(BASE_DIR, 'last_ip.txt')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

def setup_logging():
    # Remove all existing handlers cleanly to avoid pyre slice issues
    for handler in list(logging.root.handlers):
        logging.root.removeHandler(handler)
        
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOGS_DIR, f'ddns_updater_{date_str}.log')
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Keep only the latest 5 log files
    log_files = glob.glob(os.path.join(LOGS_DIR, 'ddns_updater_*.log'))
    log_files.sort(reverse=True) # Newest first
    
    # Avoid pyre slice warnings by checking length manually
    if len(log_files) > 5:
        for idx in range(5, len(log_files)):
            old_file = log_files[idx]
            try:
                os.remove(old_file)
            except Exception:
                pass

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
            
            try:
                root = ET.fromstring(result)
                err_count_node = root.find('ErrCount')
                err_count_text = err_count_node.text if err_count_node is not None else None
                err_count = int(err_count_text) if err_count_text is not None else -1
                
                if err_count == 0:
                    ip_node = root.find('IP')
                    ip_address = ip_node.text if ip_node is not None and ip_node.text else "Unknown IP"
                    logging.info(f"DDNS update successful for {record['host']}.{record['domain']}. IP set to: {ip_address}")
                    return True
                elif err_count > 0:
                    errors_node = root.find('errors')
                    error_messages = []
                    if errors_node is not None:
                        for err in errors_node:
                            if err.text:
                                error_messages.append(str(err.text))
                    reason = ", ".join(error_messages) if error_messages else "Unknown error"
                    logging.error(f"DDNS update failed for {record['host']}.{record['domain']}. Reason: {reason}")
                    return False
                else:
                    logging.warning(f"Unexpected XML response format from DDNS server for {record['host']}.{record['domain']}.")
                    return False
            except ET.ParseError:
                logging.error(f"Failed to parse DDNS response for {record['host']}.{record['domain']}.")
                return False
    except Exception as e:
        logging.error(f"Failed to update DDNS for {record['host']}.{record['domain']}: {e}")
        return False

def check_and_update(force=False):
    setup_logging()
    
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
