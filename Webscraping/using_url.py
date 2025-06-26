# File 2: extract_school_emails.py

import requests
from bs4 import BeautifulSoup
import re
import csv
from fake_useragent import UserAgent

ua = UserAgent()

def extract_emails_from_url(url):
    try:
        headers = {'User-Agent': ua.random}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        text = soup.get_text()
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return list(set(emails))
    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return []

def extract_from_csv():
    with open('school_websites.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        schools = list(reader)

    results = []
    for school in schools:
        name = school['name']
        url = school['url']
        emails = extract_emails_from_url(url)
        results.append({
            'name': name,
            'url': url,
            'emails': ', '.join(emails)
        })

    with open('school_contacts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'url', 'emails'])
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved email contacts to school_contacts.csv")


if __name__ == '__main__':
    extract_from_csv()
