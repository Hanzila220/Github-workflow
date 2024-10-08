import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
import datetime

# CSV file path to store all test results
CSV_FILE_PATH = "test_results.csv"

class TestWordpressLogin:
    def setup_method(self, method):
        # Set up headless Chrome options for CI
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1296, 696)
        self.driver.set_page_load_timeout(60)
        self.driver.set_script_timeout(30)
        self.driver.implicitly_wait(10)

        # Ensure screenshots directory exists
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def teardown_method(self, method):
        # Close the browser after each test
        self.driver.quit()

    def append_to_csv(self, results):
        """Append the test results to the CSV file."""
        if not os.path.exists(CSV_FILE_PATH):
            df = pd.DataFrame(results)
            df.to_csv(CSV_FILE_PATH, index=False)  # Write a new file if it doesn't exist
        else:
            df = pd.DataFrame(results)
            df.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)  # Append to existing file

    def test_login(self):
        start_time = time.time()
        status = "Failed"
        screenshot_path = None

        try:
            print("Navigating to login page")
            self.driver.get("https://smoothmaths.co.uk/login")

            print("Waiting for username field")
            username_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "user_login"))
            )
            username_field.send_keys("Testing")

            print("Waiting for password field")
            password_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "user_pass"))
            )
            password_field.send_keys("Testing*183258")

            print("Waiting for login button")
            login_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.ID, "wp-submit"))
            )
            login_button.click()

            print("Waiting for login result")
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("smoothmaths.co.uk")
            )

            # Check current URL
            current_url = self.driver.current_url
            print(f"Current URL after login: {current_url}")

            if current_url == "https://smoothmaths.co.uk/":
                print("Login successful")
                status = "Passed"
            else:
                print("Login failed or not redirected to the homepage")
                status = "Failed"

            # Take a screenshot
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = f"screenshots/login_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)

        except Exception as e:
            status = "Failed"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = f"screenshots/login_failed_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"Test failed due to: {e}")

        # Record end time and calculate duration
        end_time = time.time()
        duration = end_time - start_time

        # Prepare results for CSV
        results = {
            "Test Case": ["Test Login"],
            "Status": [status],
            "Duration (seconds)": [round(duration, 2)],
            "Screenshot": [screenshot_path]
        }

        # Append results to the CSV file
        self.append_to_csv(results)
