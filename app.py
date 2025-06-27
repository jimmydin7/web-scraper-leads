from flask import Flask, render_template, request, jsonify, send_file, session
import threading
import time
import urllib.parse
import re
from urllib.parse import urlparse
import pandas as pd
import io
import os
from utils import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Global variables to track scraping status
scraping_status = {
    'active': False,
    'stage': 'idle',  # idle, captcha, scraping, complete, error
    'progress': 0,
    'results': [],
    'total_found': 0,
    'message': ''
}

def get_chromedriver_path():
    """Read chromedriver path from config file"""
    try:
        with open('config.txt', 'r') as f:
            for line in f:
                if line.startswith("CHROMEDRIVER_PATH"):
                    path = line.strip().split('=', 1)[1]
                    logger.log(f'Fetched chromedriver path ({path})', 'normal')
                    return path
    except FileNotFoundError:
        logger.log("config.txt not found", "error")
        return None
    return None

def wait_for_search_results(driver, timeout=30):
    """Wait for search results to load and check if CAPTCHA is present"""
    try:
        # Wait for either search results or CAPTCHA
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, '#search') or 
                     d.find_elements(By.CSS_SELECTOR, '[src*="captcha"]') or
                     d.find_elements(By.CSS_SELECTOR, '.g-recaptcha') or
                     'captcha' in d.page_source.lower()
        )
        return True
    except TimeoutException:
        return False

def has_search_results(driver):
    """Check if the page has actual search results"""
    try:
        # Look for search result containers
        results = driver.find_elements(By.CSS_SELECTOR, '#search .g, #search .tF2Cxc, #rso .g')
        return len(results) > 0
    except:
        return False

def needs_captcha_solving(driver):
    """Check if CAPTCHA needs to be solved"""
    try:
        page_source = driver.page_source.lower()
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'verify you are human',
            'unusual traffic',
            'automated queries'
        ]
        
        for indicator in captcha_indicators:
            if indicator in page_source:
                return True
                
        # Check for CAPTCHA elements
        captcha_elements = driver.find_elements(By.CSS_SELECTOR, 
            '[src*="captcha"], .g-recaptcha, #captcha, .captcha')
        return len(captcha_elements) > 0
    except:
        return False

def scrape_leads(keywords, places):
    """Enhanced scraping function with better CAPTCHA handling and continuous scraping"""
    global scraping_status
    driver = None
    try:
        scraping_status.update({
            'active': True,
            'stage': 'initializing',
            'progress': 5,
            'message': 'Initializing scraper...'
        })
        chromedriver_path = get_chromedriver_path()
        if not chromedriver_path:
            raise Exception("Chromedriver path not configured")
        logger.log(f'Starting search for ({keywords} in {places})', 'normal')
        keyword_list = keywords.split()
        all_results = []
        email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        for place in places:
            query = ' '.join(keyword_list) + ' ' + place + ' "@gmail.com"'
            encoded_query = urllib.parse.quote_plus(query)
            logger.log(f'Generated google payload with query: {query}', 'normal')
            scraping_status.update({
                'stage': 'starting_browser',
                'progress': 10,
                'message': f'Starting browser for {place}...'
            })
            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            try:
                service = Service(executable_path=chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                logger.log(f"Couldn't start Chrome driver: {str(e)}", "error")
                raise Exception("Couldn't find chromedriver.exe. Please download the latest version and update config.txt")
            page_num = 0
            consecutive_empty_pages = 0
            max_consecutive_empty = 3
            while consecutive_empty_pages < max_consecutive_empty:
                start_index = page_num * 10
                paginated_payload = f"https://www.google.com/search?q={encoded_query}&start={start_index}"
                logger.log(f'Scraping page {page_num + 1} (start={start_index}) for {place}', 'normal')
                driver.get(paginated_payload)
                if not wait_for_search_results(driver, 30):
                    logger.log(f"Page {page_num + 1} failed to load properly", "warning")
                    consecutive_empty_pages += 1
                    page_num += 1
                    continue
                captcha_attempts = 0
                max_captcha_attempts = 5
                while needs_captcha_solving(driver) and captcha_attempts < max_captcha_attempts:
                    captcha_attempts += 1
                    scraping_status.update({
                        'stage': 'captcha',
                        'progress': 15 + (page_num * 2),
                        'message': f'CAPTCHA detected on page {page_num + 1} (attempt {captcha_attempts}). Please solve it in the browser window and wait...'
                    })
                    logger.log(f"CAPTCHA detected on page {page_num + 1}, attempt {captcha_attempts}", "warning")
                    time.sleep(15)
                    if not needs_captcha_solving(driver) and has_search_results(driver):
                        logger.log(f"CAPTCHA solved successfully on page {page_num + 1}", "normal")
                        break
                    elif captcha_attempts >= max_captcha_attempts:
                        logger.log(f"Too many CAPTCHA attempts on page {page_num + 1}, skipping", "error")
                        consecutive_empty_pages += 1
                        break
                if needs_captcha_solving(driver):
                    page_num += 1
                    continue
                if not has_search_results(driver):
                    logger.log(f"No search results found on page {page_num + 1}", "normal")
                    consecutive_empty_pages += 1
                    page_num += 1
                    continue
                consecutive_empty_pages = 0
                scraping_status.update({
                    'stage': 'scraping',
                    'progress': min(20 + (page_num * 3), 90),
                    'message': f'Scraping page {page_num + 1} for {place}...'
                })
                # Extract search results (domain + snippet)
                results_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.g, div.tF2Cxc')
                page_results = []
                seen_domains = set()
                for block in results_blocks:
                    try:
                        link_elem = block.find_element(By.CSS_SELECTOR, 'a')
                        href = link_elem.get_attribute('href')
                        if not href or 'google' in href or not href.startswith('http'):
                            continue
                        parsed = urlparse(href)
                        if not parsed.netloc:
                            continue
                        domain = f"{parsed.scheme}://{parsed.netloc}"
                        if domain in seen_domains:
                            continue
                        seen_domains.add(domain)
                        # Try to get the snippet/description
                        snippet = ''
                        try:
                            snippet_elem = block.find_element(By.CSS_SELECTOR, '.VwiC3b, .IsZvec')
                            snippet = snippet_elem.text
                        except Exception:
                            pass
                        email = '-'
                        if snippet:
                            found = email_regex.findall(snippet)
                            if found:
                                email = found[0]
                        page_results.append({'domain': domain, 'email': email, 'status': 'active'})
                    except Exception:
                        continue
                all_results.extend(page_results)
                scraping_status.update({
                    'total_found': len(all_results),
                    'message': f'Page {page_num + 1} complete. Found {len(page_results)} results (total: {len(all_results)})'
                })
                if len(page_results) == 0:
                    consecutive_empty_pages += 1
                page_num += 1
                time.sleep(2)
            driver.quit()
            driver = None
        scraping_status.update({
            'active': False,
            'stage': 'complete',
            'progress': 100,
            'results': all_results,
            'total_found': len(all_results),
            'message': f'Scraping complete! Found {len(all_results)} results.'
        })
        logger.log(f"Successfully scraped {len(all_results)} results", "normal")
        output_file = 'output.txt'
        with open(output_file, 'w') as f:
            for r in all_results:
                f.write(f"{r['domain']}\t{r['email']}\n")
        logger.log("Successfully wrote to output file.", "normal")
    except Exception as e:
        logger.log(f"Scraping error: {str(e)}", "error")
        scraping_status.update({
            'active': False,
            'stage': 'error',
            'progress': 0,
            'message': f'Error: {str(e)}'
        })
        if driver:
            try:
                driver.quit()
            except:
                pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    global scraping_status
    data = request.get_json()
    keywords = data.get('keywords', '').strip()
    places = data.get('places', [])
    if not keywords or not places or not isinstance(places, list):
        return jsonify({'error': 'Keywords and places are required'}), 400
    if scraping_status['active']:
        return jsonify({'error': 'Scraping already in progress'}), 400
    scraping_status = {
        'active': True,
        'stage': 'starting',
        'progress': 0,
        'results': [],
        'total_found': 0,
        'message': 'Starting scraping process...'
    }
    thread = threading.Thread(target=scrape_leads, args=(keywords, places))
    thread.daemon = True
    thread.start()
    return jsonify({'success': True, 'message': 'Scraping started'})

@app.route('/scraping_status')
def get_scraping_status():
    return jsonify(scraping_status)

@app.route('/download_excel')
def download_excel():
    if not scraping_status['results']:
        return jsonify({'error': 'No results to download'}), 400
    df = pd.DataFrame(scraping_status['results'])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Scraped Domains', index=False)
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='scraped_leads.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/download_txt')
def download_txt():
    if not scraping_status['results']:
        return jsonify({'error': 'No results to download'}), 400
    content = '\n'.join([f"{result['domain']}\t{result['email']}" for result in scraping_status['results']])
    output = io.StringIO()
    output.write(content)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name='scraped_leads.txt',
        mimetype='text/plain'
    )

@app.route('/get_results_text')
def get_results_text():
    if not scraping_status['results']:
        return jsonify({'error': 'No results available'}), 400
    content = '\n'.join([f"{result['domain']}\t{result['email']}" for result in scraping_status['results']])
    return jsonify({'content': content})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)