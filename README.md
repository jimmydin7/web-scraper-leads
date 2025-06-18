# Business Website Link Scraper

This Python tool uses Selenium to search Google for business websites based on a topic (keyword) and a location. It extracts and returns links to relevant websites from search results.

## 💡 What It Does

Users input a **topic** (like "barber") and a **place** (like "london"), and the script returns a list of business website links matching that query.

For example:

- **Input:** `barber` + `london`
- **Output:** 70+ links to barbershops in London

## 📦 Features

- Google search automation using Selenium
- Captures up to 90 Google results (9 pages)
- Skips duplicate domains
- Outputs results to:
  - Console
  - `output.txt` (all unique website links)
  - `output.xlsx` (if emails were being used — disabled in this version)
## How to use
1. clone repository
2. install requirements (py -m pip install -r requirements.txt)
3. install google chromedriver that matches your chrome version https://googlechromelabs.github.io/chrome-for-testing/
4. extract the .exe file and copy its poath
5. paste the .exe path on config.txt
6. Run the script 
7. enter prompted keywords and press enter after completing the captcha
