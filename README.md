# Web Scraping ESPN Cricinfo - Bowling Records

This project automates the extraction of international cricket bowling records from the ESPN Cricinfo website. Using Selenium (with undetected-chromedriver), it navigates through various statistical categories, scrapes paginated data tables, and saves the results in CSV format for further analysis.

## Features

- Scrapes more than 10 distinct bowling record tables (e.g., Most wickets, Best figures, Fastest to 100 wickets, etc.)
- Automated navigation and pagination handling for multi-page records
- Robust header and data extraction logic to handle dynamic table structures
- Saves each category as a separate CSV file in an output directory
- Handles Chrome driver stealth and modern anti-scraping measures

## Requirements

- Python 3.7+
- Google Chrome (compatible version)
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
- [selenium](https://selenium.dev/)
- pandas

Install required packages:
```bash
pip install undetected-chromedriver selenium pandas
```

## Usage

1. **Clone this repository:**
    ```bash
    git clone https://github.com/SaiKiran3640/Web-Scraping-ESPN-Cricinfo.git
    cd Web-Scraping-ESPN-Cricinfo
    ```

2. **Run the script:**
    ```bash
    python bowling.py
    ```

3. **Output:**
    - CSV files for each bowling record category will be saved to the `espncricinfo_bowling_records/` directory.

## How It Works

- The script defines a dictionary of bowling record categories and their corresponding ESPN Cricinfo URL slugs.
- For each category, it navigates to the records page, waits for the table to load, and extracts both header and data rows.
- If the table spans multiple pages, it clicks through all pages and aggregates the data.
- Each table is saved as a CSV file, with headers cleaned and data deduplicated.

## Categories Scraped

Examples of scraped categories include:

- Most wickets in career
- Best figures in an innings
- Best figures in a match
- Most wickets in a calendar year
- Most wickets in a series
- Best career bowling average
- Best career strike rate
- Fastest to 100/200/300/400/500/600/700 wickets

(See `bowling.py` → `RECORD_CATEGORIES` for the full list.)

## Notes

- Make sure your Chrome browser is installed and up-to-date.
- For headless operation, uncomment the relevant line in `setup_driver()`.
- ESPN Cricinfo may update their site structure; in case of scraping issues, review and adjust the table selectors in the script.

## Disclaimer

This project is intended **solely for educational and personal use**.

- We are **not affiliated with ESPNcricinfo** or its parent company.
- All data collected is publicly available and is not used for any commercial purpose.
- The website's robots.txt was checked at the time of development and did not explicitly disallow scraping.
- If ESPNcricinfo or any associated entity requests removal or modification of this project, we will comply promptly.

Please use responsibly and respect the terms of service of any website you interact with.

