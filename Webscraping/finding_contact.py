import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re
import time

# Read the CSV with school names and website URLs
df = pd.read_csv('school_websites.csv')
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
service = Service(r"D:\Project-ARC\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

results = []

def extract_contacts(text):
    # Simple regex for emails and phone numbers
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phones = re.findall(r"\+?\d[\d\s\-]{8,}\d", text)
    return emails, phones
 
try:
    for idx, row in df.iterrows():
        school = row['School Name']
        url = row['Website URL']
        contact_email = ""
        contact_phone = ""
        contact_address = ""

        if url != "Not found" and url.startswith("http"):
            try:
                driver.get(url)
                time.sleep(4)  # Wait for page to load

                # Get all visible text
                body_text = driver.find_element(By.TAG_NAME, "body").text

                # Extract emails and phones
                emails, phones = extract_contacts(body_text)
                contact_email = emails[0] if emails else ""
                contact_phone = phones[0] if phones else ""

                # Try to find address by looking for keywords
                address = ""
                for line in body_text.split('\n'):
                    if any(word in line.lower() for word in ["address", "addr.", "location", "contact us"]):
                        address = line.strip()
                        break
                contact_address = address

            except Exception as e:
                print(f"Error scraping {school}: {e}")

        results.append({
            "School Name": school,
            "Website URL": url,
            "Contact Email": contact_email,
            "Contact Phone": contact_phone,
            "Contact Address": contact_address
        })
        print(f"{school}: {contact_email}, {contact_phone}, {contact_address}")

finally:
    driver.quit()

# Save results to CSV
pd.DataFrame(results).to_csv('school_contacts.csv', index=False)
print("Done! Results saved to school_contacts.csv")