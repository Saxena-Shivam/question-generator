from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://saras.cbse.gov.in/saras/AffiliatedList/ListOfSchdirReport"
SCHOOL_NAME = "School"  # Change this to your desired search term

options = Options()
# Uncomment the next line to run headless (no browser window)
# options.add_argument("--headless")
service = Service(r"D:\Project-ARC\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(URL)
    wait = WebDriverWait(driver, 20)

    # Wait for the loading overlay to disappear
    wait.until(EC.invisibility_of_element_located((By.ID, "pre-load")))

    # Click the "Search by Keyword wise" radio button
    keyword_radio = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div/div/div/div[2]/form/div[1]/div/div/div[1]/label')))
    keyword_radio.click()
    # Wait for overlay again (it may reappear)
    wait.until(EC.invisibility_of_element_located((By.ID, "pre-load")))
    time.sleep(1)

    # Wait for the search box to be clickable
    search_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="InstName_orAddress"]')))
    search_box.clear()
    search_box.send_keys(SCHOOL_NAME)
    time.sleep(1)
    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div/div/div/div[2]/form/div[8]/input')))
    search_btn.click()
    # Wait for overlay after search
    wait.until(EC.invisibility_of_element_located((By.ID, "pre-load")))
    time.sleep(1)

    data = []
    while True:
        # Scrape table rows (skip header)
        rows = driver.find_elements(By.XPATH, '//table[@id="myTable"]/tbody/tr')
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if cols:
                school_data = {
                    'School Name': cols[1].text if len(cols) > 1 else '',
                    'Address': cols[2].text if len(cols) > 2 else '',
                    'Website': cols[6].text if len(cols) > 6 else '',  # Adjust index as needed
                    # Add more fields if needed
                }
                data.append(school_data)

        # Check if "Next" button is enabled
        next_btn = driver.find_element(By.XPATH, '//*[@id="myTable_next"]')
        if "disabled" in next_btn.get_attribute("class"):
            break  # No more pages
        else:
            next_btn.click()
            # Wait for overlay after clicking next
            wait.until(EC.invisibility_of_element_located((By.ID, "pre-load")))
            time.sleep(1)  # Small pause for stability

    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv('schools_scraped.csv', index=False)
    print("Scraping complete. Data saved to schools_scraped.csv.")

finally:
    driver.quit()