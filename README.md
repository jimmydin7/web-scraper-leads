# Lead Generation Pro - Web Scraping Tool

A modern, professional Flask web application for lead generation through web scraping. Designed for freelancers and businesses to find potential clients with email addresses.

## Features

- **Modern Dark UI**: Professional black-themed interface with smooth animations
- **Intelligent Search**: Target prospects by keywords and location
- **Real-time Progress**: Live updates during scraping process
- **Multiple Export Options**: Download results as Excel (.xlsx), Text (.txt), or copy to clipboard
- **CAPTCHA Handling**: Interactive browser window for solving CAPTCHAs
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download ChromeDriver:**
   - Visit https://googlechromelabs.github.io/chrome-for-testing/
   - Download the version that matches your Chrome browser
   - Place `chromedriver.exe` in the project folder
   - Update the path in `config.txt`

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Configuration

Update `config.txt` with your ChromeDriver path:
```
CHROMEDRIVER_PATH=./chromedriver.exe
```

## Usage

1. **Enter Search Criteria:**
   - Keywords: e.g., "web designer freelancer consultant"
   - Location: e.g., "New York", "London", "San Francisco"

2. **Start Scraping:**
   - Click "Start Lead Generation"
   - Solve any CAPTCHAs in the browser window that opens
   - Wait for the scraping process to complete

3. **Export Results:**
   - Download as Excel spreadsheet
   - Download as plain text file
   - Copy all results to clipboard

## How It Works

The tool searches Google for businesses/professionals in your specified location with the keywords you provide, specifically looking for pages that contain "@gmail.com" to find contact information. It extracts unique domains from the search results across multiple pages.

## Important Notes

- Make sure ChromeDriver version matches your Chrome browser version
- The tool opens a browser window for CAPTCHA solving - do not close it during scraping
- Results are automatically saved to `output.txt` in addition to the web interface
- Scraping progress is logged to `scraping.log`

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Web Scraping**: Selenium WebDriver
- **Export**: pandas, openpyxl
- **Styling**: Modern CSS with dark theme and animations

## Support

For issues or questions:
1. Check that ChromeDriver is properly configured
2. Ensure your Chrome browser is up to date
3. Verify all dependencies are installed correctly

---

Built with ❤️ for professional lead generation.