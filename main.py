from utils import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import urllib
import re

with open('config.txt', 'r') as f:
    for line in f:
        if line.startswith("CHROMEDRIVER_PATH"):
            chromedriver_path = line.strip().split('=', 1)[1]
            logger.log(f'Fetched chromedriver path ({chromedriver_path})', 'normal')

keywords = input("Enter keywords separated by spaces: ").strip()
if not keywords:
    logger.log("No keywords entered, exiting.", "warning")
    quit()

keyword_list = keywords.split()

place = input("Enter a place: ").strip()
if not place:
    logger.log("No place entered, exiting.", "warning")
    quit()

logger.log(f'Starting search for ({keywords} in {place})', 'normal')

query = ' '.join(keyword_list) + ' ' + place + ' "@gmail.com"'
encoded_query = urllib.parse.quote_plus(query)
payload = f"https://www.google.com/search?q={encoded_query}"

logger.log(f'Generated google payload ({payload})', 'normal')

try:
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)
except Exception as e:
    print(e)
    logger.log("Couldn't find chromedriver.exe to continue web scraping. Please download the latest version (https://googlechromelabs.github.io/chrome-for-testing/) and put it on config.txt. Make sure chromedriver's version is compatible with your chrome's version.",  "warning")
    quit()

from urllib.parse import urlparse
import time

known_domains = set()
all_emails = set()
for page in range(0, 90, 10):  # Fetch 8 pages
    paginated_payload = f"https://www.google.com/search?q={encoded_query}&start={page}"
    driver.get(paginated_payload)

    input("Solve captcha if needed, then press Enter...") if page == 0 else time.sleep(2)

    links = driver.find_elements(By.CSS_SELECTOR, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href and 'google' not in href:
            parsed = urlparse(href)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            if domain in known_domains:
                continue
            logger.log(f'Fetched {href}', 'normal')
            known_domains.add(domain)
    page_text = driver.page_source
    matches = re.findall(r"[a-zA-Z0-9_.+-]+@gmail\.com", page_text)
    all_emails.update(matches)

for email in sorted(all_emails):
    print("📧", email)

logger.log(f"Successfully scraped {str(len(known_domains))} links", "normal")

output_file = 'output.txt'
with open(output_file, 'w') as f:
    for domain in known_domains:
        f.write(f"{domain}\n")
    logger.log("Successfully wrote to output file.","normal")