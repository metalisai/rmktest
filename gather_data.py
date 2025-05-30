#!/usr/bin/env python3
import requests
import time
from datetime import datetime

# Most of this was written by ChatGPT (on 2. May)
# This ran unti 30. May to gather data

url = "https://transport.tallinn.ee/gps.txt"

save_dir = "tlt"
log_file = "tlt.log"

with open(log_file, "a") as logfile:
    def fetch_file():
        try:
            response = requests.get(url)
            response.raise_for_status()

            # Format: file_YYYYMMDD_HHMMSS.txt
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{save_dir}/file_{timestamp}.txt"

            with open(filename, "w", encoding='utf-8') as f:
                f.write(response.text)

            print(f"Saved: {filename}")
            logfile.write(f"Saved: {filename}\n")
        except Exception as e:
            print(f"Error fetching file: {e}")
            logfile.write(f"Error fetching file: {e}\n")
        logfile.flush()

    # Run every 60 seconds
    while True:
        fetch_file()
        time.sleep(60)
