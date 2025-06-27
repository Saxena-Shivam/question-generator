import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# Read school names from Excel
df = pd.read_excel('school.xlsx')  # Make sure your Excel file has a column named 'School Name'
school_names = df['School Name'].dropna().tolist()


options = Options()
options.add_argument("--headless")  # Remove this line if you want to see the browser
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
service = Service(r"D:\Project-ARC\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

results = []

try:
    for school in school_names:
        query = f"{school} official website"
        driver.get("https://www.bing.com/")
        time.sleep(2)
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(4)  # Wait for results to load

        url = "Not found"
        try:
            link = driver.find_element(By.CSS_SELECTOR, 'li.b_algo h2 a')
            url = link.get_attribute('href')
        except Exception:
            url = "Not found"
        results.append({'School Name': school, 'Website URL': url})
        print(f"{school}: {url}")
        time.sleep(2)  # Be polite to Bing

finally:
    driver.quit()

# Save results to CSV
pd.DataFrame(results).to_csv('school_websites.csv', index=False)
print("Done! Results saved to school_websites.csv")