import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

url = "https://spvdelhi.org/"
excel_file = "emails_found.xlsx"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", soup.get_text()))
    
    # Prepare new data
    new_data = pd.DataFrame({
        "Email": list(emails),
        "Source URL": url
    })

    # If file exists, append without duplicates
    if os.path.exists(excel_file):
        old_data = pd.read_excel(excel_file)
        combined = pd.concat([old_data, new_data], ignore_index=True)
        # Drop duplicates based on Email and Source URL
        combined = combined.drop_duplicates(subset=["Email", "Source URL"])
    else:
        combined = new_data

    combined.to_excel(excel_file, index=False)
    print(f"Found {len(emails)} emails. Updated {excel_file}")
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch the page: {e}")