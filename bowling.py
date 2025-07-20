import undetected_chromedriver as uc
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import random
import os

# --- Configuration ---
BASE_RECORDS_URL = "https://www.espncricinfo.com/records/"

RECORD_CATEGORIES = {
    "Most wickets in career": "most-wickets-in-career-93276",
    "Best figures in an innings": "best-figures-in-an-innings-283203",
    "Best figures in a match": "best-figures-in-a-match-283311",
    "Most wickets in a calendar year": "most-wickets-in-a-calendar-year-229904",
    "Most wickets in a series": "most-wickets-in-a-series-122207",
    "Best career bowling average": "best-career-bowling-average-283256",
    "Best career strike rate": "best-career-strike-rate-283274",
    "Fastest to 100 wickets": "fastest-to-100-wickets-283530",
    "Fastest to 200 wickets": "fastest-to-200-wickets-283534",
    "Fastest to 300 wickets": "fastest-to-300-wickets-283538",
    "Fastest to 400 wickets": "fastest-to-400-wickets-283542",
    "Fastest to 500 wickets": "fastest-to-500-wickets-283546",
    "Fastest to 600 wickets": "fastest-to-600-wickets-468455",
    "Fastest to 700 wickets": "fastest-to-700-wickets-468456",
    # Add any remaining categories here with their verified slugs!
}

OUTPUT_DIR = "espncricinfo_bowling_records"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- Selenium Setup ---
def setup_driver():
    """Initializes and returns an undetected_chromedriver instance."""
    options = uc.ChromeOptions()
    # options.add_argument("--headless") # Uncomment for headless mode (no browser GUI)
    # options.add_argument("--start-maximized") # Maximize window to ensure elements are visible
    
    try:
        driver = uc.Chrome(options=options)
        print("undetected-chromedriver initialized.")
        return driver
    except Exception as e:
        print(f"Error initializing undetected-chromedriver: {e}")
        print("Make sure Chrome browser is installed and compatible with your undetected-chromedriver version.")
        return None

# --- Data Extraction Functions ---
def extract_table_data(driver, category_name):
    """
    Extracts data from the main statistical table on the current page,
    including robust header scraping.
    """
    data = []
    headers = []

    try:
        table_full_class_selector = "table.ds-w-full.ds-table.ds-table-xs.ds-table-auto.ds-w-full.ds-overflow-scroll.ds-scrollbar-hide"
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, table_full_class_selector)))
        
        main_table = driver.find_element(By.CSS_SELECTOR, table_full_class_selector)
        
        if not main_table:
            print(f"Warning: Main statistics table not found for {category_name}.")
            return pd.DataFrame()

        # --- Header Extraction Logic ---
        try:
            # Look for the header row within the thead section
            header_row_locator = (By.CSS_SELECTOR, "thead.ds-bg-fill-content-alternate tr")
            WebDriverWait(main_table, 10).until(EC.presence_of_element_located(header_row_locator))
            header_row = main_table.find_element(*header_row_locator)
            
            # Try to find <th> elements first
            header_elements = header_row.find_elements(By.TAG_NAME, "th")

            # If no <th> elements, try finding <td> elements (sometimes they are used as headers)
            if not header_elements:
                header_elements = header_row.find_elements(By.TAG_NAME, "td")
            
            if header_elements:
                for header_el in header_elements:
                    header_text = header_el.text.strip()
                    
                    # If direct text is empty, check for common nested elements (like <span> for sortable headers)
                    if not header_text:
                        try:
                            # Look for a span directly inside the header element
                            nested_span = header_el.find_element(By.TAG_NAME, "span")
                            header_text = nested_span.text.strip()
                        except NoSuchElementException:
                            pass # No span, continue
                    
                    # If still no text, or if the header contains an icon/complex structure,
                    # you might need more specific logic. For now, we'll take what we get.
                    
                    # Clean up common unwanted characters like '\n' from sort indicators
                    header_text = header_text.split('\n')[0].strip()

                    headers.append(header_text)
                print(f"Successfully scraped headers for {category_name}: {headers}")
            else:
                print(f"Warning: No valid header elements (th or td) found within thead for {category_name}.")

        except (NoSuchElementException, TimeoutException) as e:
            print(f"Warning: Thead or header row not found or timed out for {category_name}. Error: {e}")
        
        if not headers:
            print(f"Warning: Headers could not be scraped for {category_name}. Data will be saved without specific column names.")
            # If headers are still empty, we'll proceed without them and let Pandas assign defaults.

        # Add headers as the first row for the DataFrame if successfully scraped
        # If headers are empty, this won't be added, and pd.DataFrame(data_rows) will get default numeric columns
        if headers:
            data.append(headers)

        # --- Body Row Extraction ---
        body_rows_locator = (By.CSS_SELECTOR, "tbody tr")
        WebDriverWait(main_table, 10).until(EC.presence_of_element_located(body_rows_locator))
        body_rows = main_table.find_elements(*body_rows_locator)
        
        if not body_rows:
            print(f"Warning: No <tbody> rows found for {category_name}.")

        for row in body_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                row_data = [cell.text.strip() for cell in cells]
                data.append(row_data)

        # Prepare data for DataFrame
        if len(data) > (1 if headers else 0): # Check if there's data beyond just headers (if headers exist)
            num_data_rows = len(data) - (1 if headers else 0)
            print(f"Extracted {num_data_rows} data rows for {category_name}.")
            
            # If headers were scraped, use them. Otherwise, Pandas will use default integer columns.
            if headers:
                # Ensure all data rows have the same number of columns as headers
                max_cols = len(headers)
                processed_data = []
                for row_list in data[(1 if headers else 0):]: # Skip the first row if it contains scraped headers
                    if len(row_list) > max_cols:
                        processed_data.append(row_list[:max_cols]) # Trim extra columns
                    elif len(row_list) < max_cols:
                        processed_data.append(row_list + [''] * (max_cols - len(row_list))) # Pad missing columns
                    else:
                        processed_data.append(row_list)
                return pd.DataFrame(processed_data, columns=headers)
            else:
                # If headers couldn't be scraped, just return the data rows. Pandas will assign numeric columns.
                return pd.DataFrame(data)
        else:
            print(f"No actual data rows found after processing for {category_name}.")
            return pd.DataFrame()

    except NoSuchElementException as e:
        print(f"Error: Element not found for {category_name} (URL: {driver.current_url}): {e}")
        return pd.DataFrame()
    except TimeoutException:
        print(f"Error: Timeout waiting for table/elements for {category_name} on {driver.current_url}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred while extracting table for {category_name}: {e}")
        return pd.DataFrame()

def extract_paginated_table_data(driver, category_name, base_record_url_unused): # Renamed for clarity
    """
    Handles navigation through pages and aggregates data from all pages.
    """
    all_data_frames = []
    current_page = 1
    
    NEXT_BUTTON_SELECTOR = (By.XPATH, "//div[contains(@class, 'ds-pagination')]//a[contains(@class, 'ds-popper-link') and span[contains(text(), 'Next')]]")
    
    while True:
        print(f"Processing page {current_page} for {category_name}...")
        
        current_df = extract_table_data(driver, f"{category_name} (Page {current_page})")
        
        if not current_df.empty:
            all_data_frames.append(current_df)
        else:
            print(f"No data or error on page {current_page} for {category_name}. Stopping pagination.")
            break

        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(NEXT_BUTTON_SELECTOR)
            )
            
            if "ds-cursor-not-allowed" in next_button.get_attribute("class"): 
                print(f"Next button found but disabled for {category_name}. Assuming last page.")
                break
            
            next_button.click()
            current_page += 1
            time.sleep(random.uniform(3, 6))

        except (TimeoutException, NoSuchElementException):
            print(f"No clickable 'Next' button found for {category_name}. Assuming last page.")
            break
        except WebDriverException as e:
            print(f"WebDriver error while clicking next page for {category_name}: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred while handling pagination for {category_name}: {e}")
            break

    if all_data_frames:
        combined_df = pd.concat(all_data_frames, ignore_index=True)
        combined_df.drop_duplicates(inplace=True)
        return combined_df
    return pd.DataFrame()

# --- Main Execution ---
if __name__ == "__main__":
    driver = None
    try:
        driver = setup_driver()
        if driver is None:
            exit("Driver setup failed. Exiting.")

        for category_name, slug in RECORD_CATEGORIES.items():
            full_url = f"{BASE_RECORDS_URL}{slug}"
            print(f"\n--- Processing: {category_name} ({full_url}) ---")

            try:
                driver.get(full_url)
                time.sleep(random.uniform(4, 8))

                df_records = extract_paginated_table_data(driver, category_name, full_url)

                if not df_records.empty:
                    filename_safe_category = category_name.replace(' ', '_').replace('/', '_').replace(':', '')
                    filename = os.path.join(OUTPUT_DIR, f"espncricinfo_test_bowling_{filename_safe_category}.csv")
                    # When `columns` are passed to DataFrame, Pandas automatically uses them as headers.
                    # So, we just need index=False to prevent the DataFrame index from being written.
                    df_records.to_csv(filename, index=False, encoding='utf-8')
                    print(f"Saved {len(df_records)} records to {filename}")
                else:
                    print(f"No records found or extracted for {category_name}.")

            except WebDriverException as e:
                print(f"WebDriver error navigating to {full_url}: {e}")
                print("This might indicate the browser crashed or lost connection. Attempting to continue...")
            except Exception as e:
                print(f"An error occurred while processing {category_name}: {e}")

            time.sleep(random.uniform(15, 30))

    except Exception as e:
        print(f"An unhandled error occurred during the main process: {e}")
    finally:
        if driver:
            print("Quitting browser...")
            driver.quit()
            print("Browser closed.")