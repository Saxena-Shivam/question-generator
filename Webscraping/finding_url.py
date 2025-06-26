import requests
from bs4 import BeautifulSoup
import csv
import re

SOURCE_URL = 'https://saras.cbse.gov.in/saras/AffiliatedList/ListOfSchdirReport'

def extract_emails_from_url(url):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        # Simple regex for emails
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return list(set(emails))
    except Exception as e:
        return []

def get_school_websites_and_emails():
    response = requests.get(SOURCE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    schools = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        name = link.get_text(strip=True)
        if 'school' in href or '.edu' in href or '.ac.in' in href:
            url = href if href.startswith('http') else 'https://' + href.strip('/')
            emails = extract_emails_from_url(url)
            schools.append({
                'name': name,
                'url': url,
                'emails': ', '.join(emails) if emails else ''
            })

    with open('school_websites_and_emails.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'url', 'emails'])
        writer.writeheader()
        writer.writerows(schools)

    print(f"Saved {len(schools)} school websites and emails to school_websites_and_emails.csv")

if __name__ == '__main__':
    get_school_websites_and_emails()